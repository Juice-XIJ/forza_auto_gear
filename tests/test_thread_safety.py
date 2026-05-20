"""Regression test for the thread-safety fix in MainWindow.

The bug being guarded: Forza worker threads and the pynput listener
thread used to call Tk widget methods directly, which is unsafe.
After the fix, all such calls go through ``ui_queue.call_on_main`` /
``ui_queue.enqueue``. This test fires a large number of enqueues from
multiple background threads and verifies the queue drains cleanly on
the main thread without exceptions.
"""

from __future__ import annotations

import threading
import time

import pytest

from update_queue import TkUpdateQueue


def test_concurrent_enqueue_drains_cleanly(tk_root):
    queue = TkUpdateQueue(tk_root, interval_ms=2)
    queue.start()

    received: list[tuple[int, int]] = []
    lock = threading.Lock()

    def append(thread_id: int, value: int) -> None:
        # No external Tk interaction here; this runs on the main thread
        # via the pump, so direct list append is fine.
        with lock:
            received.append((thread_id, value))

    NUM_THREADS = 4
    PER_THREAD = 10_000
    barrier = threading.Barrier(NUM_THREADS)

    def worker(thread_id: int) -> None:
        barrier.wait()
        for i in range(PER_THREAD):
            queue.enqueue(append, thread_id, i)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Drive the pump until the queue empties or 5 s elapse.
    deadline = time.time() + 5.0
    while queue.pending() > 0 and time.time() < deadline:
        tk_root.update()
        time.sleep(0.001)

    queue.stop()

    assert queue.pending() == 0, "queue did not drain in time"
    assert len(received) == NUM_THREADS * PER_THREAD
    # Each (thread_id, value) pair must appear exactly once.
    assert len(set(received)) == NUM_THREADS * PER_THREAD


def test_main_thread_call_runs_inline(tk_root):
    """``call_on_main`` from the main thread runs the callback inline
    (no pump-tick needed); this is what lets unit tests stay synchronous.
    """
    queue = TkUpdateQueue(tk_root)
    queue.start()

    seen: list[int] = []
    queue.call_on_main(seen.append, 1)
    queue.call_on_main(seen.append, 2)

    # No pump call yet — both must already have run inline.
    assert seen == [1, 2]
    queue.stop()


def test_background_thread_call_is_deferred(tk_root):
    """``call_on_main`` from a *non*-main thread must enqueue, not run
    inline. Otherwise we'd still be touching Tk from a worker.
    """
    queue = TkUpdateQueue(tk_root)
    queue.start()

    seen: list[int] = []

    def worker():
        queue.call_on_main(seen.append, 99)

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    # Worker has finished, but the pump hasn't been driven, so the
    # callback must still be queued, not executed.
    assert seen == []
    assert queue.pending() == 1

    queue.pump_once()
    assert seen == [99]
    queue.stop()
