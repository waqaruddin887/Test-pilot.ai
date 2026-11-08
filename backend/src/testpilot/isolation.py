"""Trusted supervisor: clean environment, finite command, resource/time/output bounds."""

import asyncio
import importlib.util
import json
import os
import resource
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BROWSERS = Path(
    os.environ.get("PLAYWRIGHT_BROWSERS_PATH", Path.home() / ".cache/ms-playwright")
).resolve()


def command_line(defective: bool = False, include_reference: bool = False) -> list[str]:
    packages = set()
    for name in [
        "playwright",
        "pydantic",
        "pydantic_core",
        "typing_extensions",
        "annotated_types",
        "typing_inspection",
        "greenlet",
        "pyee",
    ]:
        spec = importlib.util.find_spec(name)
        if spec and spec.origin:
            packages.add(
                str(
                    Path(spec.origin).parent
                    if spec.submodule_search_locations is None
                    else Path(spec.origin).parent.parent
                )
            )
    args = [
        "unshare",
        "--user",
        "--map-current-user",
        "--net",
        "bwrap",
        "--die-with-parent",
        "--new-session",
        "--unshare-pid",
        "--ro-bind",
        "/usr",
        "/usr",
        "--symlink",
        "usr/lib",
        "/lib",
        "--symlink",
        "usr/lib64",
        "/lib64",
        "--dir",
        "/app",
        "--dir",
        "/app/testpilot",
        "--ro-bind",
        str(ROOT / "fixtures" / ("defective" if defective else "good")),
        "/fixtures/site",
        "--ro-bind",
        str(ROOT / "fixtures/requirements"),
        "/fixtures/requirements",
        "--ro-bind",
        str(BROWSERS),
        "/browsers",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--size",
        "268435456",
        "--tmpfs",
        "/tmp",
    ]
    modules = ["__init__", "browser", "contracts", "fixtures", "policy"]
    if include_reference:
        modules.append("reference")
    for name in modules:
        args += [
            "--ro-bind",
            str(ROOT / f"backend/src/testpilot/{name}.py"),
            f"/app/testpilot/{name}.py",
        ]
    search = ["/app"]
    for index, path in enumerate(sorted(packages)):
        mount = f"/deps{index}"
        args += ["--ro-bind", path, mount]
        search.append(mount)
    args += [
        "--setenv",
        "HOME",
        "/tmp",
        "--setenv",
        "PYTHONPATH",
        ":".join(search),
        "--setenv",
        "PLAYWRIGHT_BROWSERS_PATH",
        "/browsers",
        "--setenv",
        "TESTPILOT_FIXTURES",
        "/fixtures",
        "--setenv",
        "TESTPILOT_ISOLATED",
        "1",
        sys.executable if sys.executable.startswith("/usr/") else "/usr/bin/python3",
        "-m",
        "testpilot.browser",
    ]
    return args


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (45, 45))
    resource.setrlimit(resource.RLIMIT_FSIZE, (12 * 1024 * 1024, 12 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (512, 512))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def process_usage(root_pid: int) -> tuple[int, int]:
    pending, seen, rss_kib = [root_pid], set(), 0
    while pending:
        pid = pending.pop()
        if pid in seen:
            continue
        seen.add(pid)
        try:
            pending.extend(
                int(value) for value in Path(f"/proc/{pid}/task/{pid}/children").read_text().split()
            )
            for line in Path(f"/proc/{pid}/status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    rss_kib += int(line.split()[1])
        except FileNotFoundError:
            continue
    return len(seen), rss_kib


async def invoke(command: dict, cancelled=None, timeout: float = 40) -> dict:
    command = {**command, "parent_namespace": os.readlink("/proc/self/ns/net")}
    args = command_line(
        defective=bool(command.get("defective")),
        include_reference=command.get("kind") == "reference",
    )
    command.pop("defective", None)
    payload = json.dumps(command).encode()
    if len(payload) > 262144:
        raise ValueError("command too large")
    process = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
        start_new_session=True,
        preexec_fn=limits,
    )

    async def communicate():
        process.stdin.write(payload)
        await process.stdin.drain()
        process.stdin.close()

        async def bounded(stream, ceiling):
            data = bytearray()
            while chunk := await stream.read(65536):
                data.extend(chunk)
                if len(data) > ceiling:
                    raise RuntimeError("runner output quota exceeded")
            return bytes(data)

        output, errors = await asyncio.gather(
            bounded(process.stdout, 12 * 1024 * 1024), bounded(process.stderr, 16384)
        )
        await process.wait()
        if process.returncode:
            raise RuntimeError(
                "isolated_runner_unavailable:" + errors.decode(errors="replace")[:200]
            )
        return json.loads(output)

    task = asyncio.create_task(communicate())
    started = asyncio.get_running_loop().time()
    try:
        while not task.done():
            if cancelled and cancelled():
                raise asyncio.CancelledError()
            if asyncio.get_running_loop().time() - started > timeout:
                raise TimeoutError("isolated runner deadline")
            processes, rss_kib = process_usage(process.pid)
            if processes > 64 or rss_kib > 1024 * 1024:
                raise RuntimeError("runner resource budget exceeded")
            await asyncio.sleep(0.1)
        return await task
    finally:
        if process.returncode is None:
            os.killpg(process.pid, signal.SIGKILL)
            await asyncio.wait_for(process.wait(), 5)
        if not task.done():
            task.cancel()
            try:
                await task
            except BaseException:
                pass
