"""Real UI → API → restricted worker test, with disposable local data and test credentials."""

import asyncio
import os
import signal
import subprocess
import tempfile
from pathlib import Path

import httpx
from playwright.async_api import async_playwright, expect
from testpilot.db import Base, OracleVersion, Slot, database
from testpilot.fixtures import ORACLES, SOURCE_HASH


async def test_ui():
    runtime = Path(".runtime").resolve()
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ui-test-", dir=runtime) as temporary:
        directory = Path(temporary)
        url = "sqlite:///" + str(directory / "ui.db")
        engine, sessions = database(url)
        Base.metadata.create_all(engine)
        with sessions.begin() as db:
            db.add(Slot(id=1))
            for ref, oracle in ORACLES.items():
                db.add(OracleVersion(id=ref, specification=oracle, source_sha256=SOURCE_HASH))
        environment = {
            **os.environ,
            "TESTPILOT_DATABASE_URL": url,
            "TESTPILOT_DATA_DIR": str(directory),
            "TESTPILOT_OPERATOR_SECRET": "ui-test-secret-" + "s" * 32,
            "TESTPILOT_CLI_TOKEN": "ui-test-cli-" + "c" * 32,
            "TESTPILOT_UI_ORIGIN": "http://localhost:3000",
            "NEXT_TELEMETRY_DISABLED": "1",
        }
        processes = []
        logs = []
        try:
            for name, command in [
                (
                    "api",
                    [
                        ".venv/bin/python",
                        "-m",
                        "uvicorn",
                        "testpilot.api:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8000",
                    ],
                ),
                ("worker", [".venv/bin/python", "-m", "testpilot.worker"]),
                ("web", ["pnpm", "--filter", "@testpilot/web", "start"]),
            ]:
                log = (directory / (name + ".log")).open("w+")
                logs.append(log)
                processes.append(
                    subprocess.Popen(
                        command,
                        env=environment,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
                )
            async with httpx.AsyncClient() as client:
                for _ in range(150):
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError("development service exited")
                    try:
                        ready = await client.get(
                            "http://127.0.0.1:8000/api/ready",
                            headers={
                                "Authorization": "Bearer " + environment["TESTPILOT_CLI_TOKEN"]
                            },
                        )
                        web = await client.get("http://localhost:3000")
                        if ready.status_code == 200 and web.status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    await asyncio.sleep(0.2)
                else:
                    raise RuntimeError("local services did not become ready")
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(chromium_sandbox=True)
                page = await browser.new_page(viewport={"width": 1440, "height": 1080})
                await page.route(
                    "**/*",
                    lambda route: (
                        route.continue_()
                        if route.request.url.startswith(
                            ("http://localhost:3000/", "http://127.0.0.1:8000/")
                        )
                        else route.abort()
                    ),
                )
                await page.goto("http://localhost:3000")
                await expect(
                    page.get_by_role("heading", name="Unlock local workspace")
                ).to_be_visible()
                await page.get_by_label("Operator secret").fill(
                    environment["TESTPILOT_OPERATOR_SECRET"]
                )
                await page.get_by_role("button", name="Unlock", exact=True).click()
                await expect(
                    page.get_by_role("heading", name="Create approved project")
                ).to_be_visible()
                await page.get_by_label("Project name").fill("Browser E2E seeded fixture")
                await page.get_by_label("Repository fixture").select_option("synthetic-seeded-v1")
                await page.get_by_role("button", name="Create project", exact=True).click()
                await expect(
                    page.get_by_role("heading", name="Browser E2E seeded fixture")
                ).to_be_visible()
                await page.screenshot(path=str(runtime / "dashboard-desktop.png"), full_page=True)
                await page.set_viewport_size({"width": 390, "height": 844})
                await page.screenshot(path=str(runtime / "dashboard-mobile.png"), full_page=True)
                assert await page.evaluate(
                    "document.documentElement.scrollWidth <= window.innerWidth"
                ), "mobile overflow"
                await page.set_viewport_size({"width": 1440, "height": 1080})
                await (
                    page.get_by_role("navigation")
                    .get_by_role("link", name="New test run", exact=True)
                    .click()
                )
                await page.get_by_role("button", name="Start fixture run", exact=True).click()
                await expect(page.get_by_text("completed", exact=True).first).to_be_visible(
                    timeout=45000
                )
                await page.get_by_role("link").filter(has_text="FORM-001@1").click()
                await expect(
                    page.get_by_role("heading", name="Independent oracle", exact=True)
                ).to_be_visible()
                await expect(
                    page.get_by_text("Both attempts have current integrity-checked evidence.")
                ).to_be_visible()
                assert await page.locator("img").count() == 2
                await page.screenshot(path=str(runtime / "finding-desktop.png"), full_page=True)
                await expect(
                    page.get_by_role("button", name="Accept verified finding")
                ).to_be_disabled()
                print(
                    "PASS: UI login, project creation, run submission, real worker execution, seeded finding, evidence previews, mobile width and review gate."
                )
                await browser.close()
        except Exception:
            for log in logs:
                log.flush()
                log.seek(0)
                print(log.read()[-2500:])
            raise
        finally:
            for process in processes:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
            for process in processes:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
            for log in logs:
                log.close()
            engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_ui())
