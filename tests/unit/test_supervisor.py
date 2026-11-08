from pathlib import Path

from testpilot.isolation import process_usage


def test_proc_exit_during_watchdog_read_is_not_an_execution_error(monkeypatch):
    def vanished(*args, **kwargs):
        raise ProcessLookupError("process exited during /proc read")

    monkeypatch.setattr(Path, "read_text", vanished)
    count, rss = process_usage(12345)
    assert count == 1
    assert rss == 0
