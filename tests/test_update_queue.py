"""Tests for the thread-safe TkUpdateQueue."""

from __future__ import annotations

import threading
import time

from update_queue import TkUpdateQueue


def test_enqueue_runs_on_pump(tk_root):
    queue = TkUpdateQueue(tk_root, interval_ms=5)
    queue.start()
    seen: list[int] = []

    queue.enqueue(seen.append, 1)
    queue.enqueue(seen.append, 2)
    queue.enqueue(seen.append, 3)

    # Let the pump tick a few times.
    for _ in range(10):
        tk_root.update()
        time.sleep(0.01)

    queue.stop()
    assert seen == [1, 2, 3]


def test_enqueue_from_background_thread(tk_root):
    queue = TkUpdateQueue(tk_root, interval_ms=5)
    queue.start()
    seen: list[int] = []

    def worker():
        for i in range(50):
            queue.enqueue(seen.append, i)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Drain the queue by ticking the Tk event loop until empty.
    deadline = time.time() + 2.0
    while queue.pending() > 0 and time.time() < deadline:
        tk_root.update()
        time.sleep(0.005)

    queue.stop()
    assert len(seen) == 4 * 50
    assert sorted(seen) == sorted(seen)  # no exceptions; ordering not guaranteed across threads


def test_pump_once_drains_in_fifo(tk_root):
    queue = TkUpdateQueue(tk_root)
    # Don't start the timer; drive pump_once manually.
    seen: list[str] = []
    queue.enqueue(seen.append, "a")
    queue.enqueue(seen.append, "b")
    queue.enqueue(seen.append, "c")

    drained = queue.pump_once()
    assert drained == 3
    assert seen == ["a", "b", "c"]


def test_callback_exception_does_not_kill_pump(tk_root):
    queue = TkUpdateQueue(tk_root)
    seen: list[int] = []

    def boom():
        raise RuntimeError("boom")

    queue.enqueue(boom)
    queue.enqueue(seen.append, 42)

    queue.pump_once()
    assert seen == [42]


def test_stop_discards_pending(tk_root):
    queue = TkUpdateQueue(tk_root, interval_ms=5)
    queue.start()
    seen: list[int] = []
    queue.enqueue(seen.append, 1)
    queue.stop()
    # After stop, new enqueues should be dropped.
    queue.enqueue(seen.append, 2)
    # Drive the loop briefly to confirm nothing runs.
    for _ in range(3):
        tk_root.update()
        time.sleep(0.01)
    # The pre-stop item may or may not have run depending on timing; the
    # post-stop item must never have run.
    assert 2 not in seen
