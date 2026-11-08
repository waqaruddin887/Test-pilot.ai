"""Isolated child only. Accepts finite commands, writes bounded JSON to stdout."""

import asyncio
import base64
import hashlib
import json
import os
import socket
import sys
import time
from pathlib import Path

from playwright.async_api import TimeoutError as BrowserTimeout
from playwright.async_api import async_playwright, expect

from testpilot.contracts import AssertUrl, AssertVisible, Click, Fill, Navigate
from testpilot.fixtures import html
from testpilot.policy import ORIGIN, parse_plan, request_allowed, validate_plan


def network_probe(parent_namespace: str) -> dict:
    namespace = os.readlink("/proc/self/ns/net")
    if namespace == parent_namespace:
        raise RuntimeError("network namespace isolation missing")
    denied = []
    for host in ["127.0.0.1", "169.254.169.254", "10.0.0.1", "1.1.1.1", "::1"]:
        family = socket.AF_INET6 if ":" in host else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.15)
            try:
                sock.connect((host, 80))
            except OSError:
                denied.append(host)
            else:
                raise RuntimeError("network destination unexpectedly reachable")
    if (
        Path("/home/waqar").exists()
        or Path("/app/testpilot/api.py").exists()
        or Path("/app/testpilot/planner.py").exists()
        or os.environ.get("TESTPILOT_OPERATOR_SECRET")
    ):
        raise RuntimeError("host private files or credentials exposed")
    return {"namespace_distinct": True, "denied_destinations": denied, "private_home_absent": True}


def locator(page, target):
    if target.kind == "role":
        return page.get_by_role(target.role, name=target.name, exact=True)
    return page.get_by_text(target.text, exact=True)


async def main(command: dict) -> dict:
    proof = network_probe(command["parent_namespace"])
    kind = command["kind"]
    if kind not in {"probe", "discover", "execute", "reference", "adversarial"}:
        raise ValueError("unsupported command")
    defective = command.get("defective", False)
    blocked = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(chromium_sandbox=True, headless=True)
        context = await browser.new_context(
            service_workers="block", accept_downloads=False, viewport={"width": 1000, "height": 720}
        )

        async def route(request_route):
            request = request_route.request
            if request_allowed(request.url, request.method):
                from urllib.parse import urlsplit

                await request_route.fulfill(
                    status=200,
                    content_type="text/html",
                    body=html(urlsplit(request.url).path, defective),
                    headers={
                        "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'"
                    },
                )
            else:
                blocked.append("policy_blocked")
                await request_route.abort("blockedbyclient")

        await context.route("**/*", route)
        await context.route_web_socket("**/*", lambda ws: ws.close())
        context.on("page", lambda page: page.on("popup", lambda popup: popup.close()))
        page = await context.new_page()
        page.on("dialog", lambda dialog: dialog.dismiss())
        page.on("download", lambda download: download.cancel())
        if kind == "probe":
            await page.goto(ORIGIN + "/form")
            result = {"proof": proof, "browser": browser.version, "title": await page.title()}
        elif kind == "adversarial":
            await page.goto(ORIGIN + "/form")
            # Fixed security probes. Each attempted navigation must be rejected by routing.
            for url in ["http://127.0.0.1/", "http://169.254.169.254/", "https://example.com/"]:
                try:
                    await page.goto(url, timeout=1000)
                except Exception:
                    pass
                else:
                    raise RuntimeError("off_origin_navigation_executed")
            if len(blocked) != 3:
                raise RuntimeError("browser_request_denials_missing")
            result = {"proof": proof, "blocked_requests": len(blocked), "violations_executed": 0}
        elif kind == "discover":
            from testpilot.policy import path_allowed

            await page.goto(ORIGIN + path_allowed(command["target_path"]))
            outline = []
            for role in ["button", "link", "textbox", "heading"]:
                loc = page.get_by_role(role)
                for i in range(min(await loc.count(), 50)):
                    item = loc.nth(i)
                    name = (
                        await item.get_attribute("aria-label")
                        if role == "textbox"
                        else await item.inner_text()
                    )
                    outline.append({"role": role, "name": (name or "")[:256]})
            result = {
                "title": (await page.title())[:256],
                "path": command["target_path"],
                "outline": outline[:500],
                "text": (await page.locator("main").inner_text())[:8000],
                "proof": proof,
            }
        elif kind == "reference":
            from testpilot.reference import check

            result = await check(page, command["target_path"])
        else:
            plan = parse_plan(json.dumps(command["plan"]).encode())
            validate_plan(plan, command["objective"], command["target_path"], command["max_cases"])
            if len(plan.cases) != 1:
                raise ValueError("isolated command accepts one case")
            await context.tracing.start(screenshots=True, snapshots=True, sources=False)
            results = []
            status = "pass"
            for step in plan.cases[0].steps:
                started = time.monotonic()
                item = {"step_id": step.id, "action": step.action, "status": "passed"}
                try:
                    timeout = min(step.timeout_ms, 5000 if isinstance(step, Navigate) else 2000)
                    if isinstance(step, Navigate):
                        await page.goto(ORIGIN + step.path, timeout=timeout)
                    elif isinstance(step, (Click, Fill)):
                        target = locator(page, step.target)
                        if await target.count() != 1:
                            raise ValueError("ambiguous_or_missing_action_locator")
                        if isinstance(step, Click):
                            await target.click(timeout=timeout)
                        else:
                            await target.fill(step.value, timeout=timeout)
                    elif isinstance(step, AssertVisible):
                        target = locator(page, step.target)
                        if await target.count() > 1:
                            raise ValueError("ambiguous_assertion_locator")
                        await expect(target).to_be_visible(timeout=timeout)
                    elif isinstance(step, AssertUrl):
                        await expect(page).to_have_url(ORIGIN + step.path, timeout=timeout)
                    if blocked or await context.cookies():
                        raise ValueError("policy_blocked_or_sensitive_state")
                except (AssertionError, BrowserTimeout):
                    if isinstance(step, (AssertVisible, AssertUrl)) and not blocked:
                        item["status"] = "assertion_failed"
                        item["oracle_ref"] = step.oracle_ref
                        status = "suspected" if step.oracle_ref else "inconclusive"
                    else:
                        item["status"] = "test_error"
                        status = "test_error"
                except ValueError as error:
                    item["status"] = "test_error"
                    item["category"] = str(error)
                    status = "test_error"
                item["duration_ms"] = round((time.monotonic() - started) * 1000, 3)
                if isinstance(step, (AssertVisible, AssertUrl)):
                    item["expected"] = step.model_dump(exclude={"id", "timeout_ms"})
                    item["observed"] = {
                        "path": page.url.removeprefix(ORIGIN),
                        "visible_text": (await page.locator("main").inner_text())[:4000],
                    }
                results.append(item)
                if item["status"] != "passed":
                    break
            screenshot = await page.screenshot(type="png")
            await context.tracing.stop(path="/tmp/attempt.zip")
            trace = Path("/tmp/attempt.zip").read_bytes()
            if len(screenshot) + len(trace) > 8 * 1024 * 1024:
                raise ValueError("artifact quota exceeded")
            artifacts = [
                {
                    "kind": kind_,
                    "data": base64.b64encode(data).decode(),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
                for kind_, data in [("screenshot", screenshot), ("trace", trace)]
            ]
            if plan.cases[0].intent == "exploratory":
                status = "inconclusive" if status != "test_error" else status
            result = {
                "assessment": status,
                "steps": results,
                "artifacts": artifacts,
                "proof": proof,
                "browser": browser.version,
                "reset_version": "static-fresh-context-1",
            }
        await context.close()
        await browser.close()
        return result


if __name__ == "__main__":
    try:
        raw = sys.stdin.buffer.read(262145)
        if len(raw) > 262144:
            raise ValueError("command too large")
        output = asyncio.run(main(json.loads(raw)))
        encoded = json.dumps(output)
        if len(encoded) > 12 * 1024 * 1024:
            raise ValueError("result too large")
        sys.stdout.write(encoded)
    except Exception as error:
        # Diagnostics stay local; never include page data or environment variables.
        sys.stderr.write(f"runner_failure:{type(error).__name__}\n")
        sys.exit(1)
