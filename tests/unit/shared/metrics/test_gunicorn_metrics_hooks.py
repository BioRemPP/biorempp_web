"""Unit tests for Gunicorn metric hooks in multiprocess mode."""

from __future__ import annotations

from types import SimpleNamespace

import gunicorn_config
from src.shared.metrics import WORKERS_ACTIVE, WORKER_REQUESTS_TOTAL


class _DummyLogger:
    @staticmethod
    def debug(*args, **kwargs) -> None:
        return None

    @staticmethod
    def warning(*args, **kwargs) -> None:
        return None


class _DummyWorker:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.log = _DummyLogger()


class _DummyRequest:
    def __init__(self, method: str = "POST", path: str = "/_dash-update-component") -> None:
        self.method = method
        self.path = path
        self.headers = {"Content-Length": "256"}


def _counter_value(counter, **labels) -> float:
    return float(counter.labels(**labels)._value.get())


def test_on_starting_cleans_prometheus_multiproc_dir(monkeypatch, tmp_path) -> None:
    multiproc_dir = tmp_path / "prom-multiproc"
    multiproc_dir.mkdir(parents=True, exist_ok=True)
    (multiproc_dir / "old_a.db").write_text("old-a", encoding="utf-8")
    (multiproc_dir / "old_b.db").write_text("old-b", encoding="utf-8")
    stale_subdir = multiproc_dir / "stale-subdir"
    stale_subdir.mkdir(parents=True, exist_ok=True)
    (stale_subdir / "junk.txt").write_text("junk", encoding="utf-8")

    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", str(multiproc_dir))

    gunicorn_config.on_starting(SimpleNamespace())

    assert multiproc_dir.exists()
    assert list(multiproc_dir.iterdir()) == []


def test_child_exit_marks_process_dead_when_multiproc_enabled(
    monkeypatch, tmp_path
) -> None:
    multiproc_dir = tmp_path / "prom-multiproc"
    multiproc_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", str(multiproc_dir))

    calls: list[int] = []

    class _FakeMultiprocess:
        @staticmethod
        def mark_process_dead(pid: int) -> None:
            calls.append(pid)

    monkeypatch.setattr(gunicorn_config, "prom_multiprocess", _FakeMultiprocess())

    gunicorn_config.child_exit(SimpleNamespace(), _DummyWorker(pid=4321))

    assert calls == [4321]


def test_worker_hooks_emit_request_and_active_metrics() -> None:
    worker = _DummyWorker(pid=777)
    before_requests = _counter_value(WORKER_REQUESTS_TOTAL, worker_pid="777")

    gunicorn_config.post_fork(SimpleNamespace(), worker)
    gunicorn_config.pre_request(worker, _DummyRequest())

    assert float(WORKERS_ACTIVE._value.get()) >= 1.0
    assert _counter_value(WORKER_REQUESTS_TOTAL, worker_pid="777") >= (
        before_requests + 1.0
    )
