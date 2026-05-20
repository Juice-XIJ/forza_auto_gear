"""Thread-safe queue for marshaling UI updates onto the Tk main thread.

``tkinter`` is not thread-safe: widgets must only be touched from the
thread that constructed the ``Tk`` interpreter. The Forza app reads UDP
telemetry on background workers and receives global keyboard events on
a pynput listener thread; both want to update widgets.

This module provides a small ``TkUpdateQueue`` that lets background
threads enqueue closures which are then drained on the main thread by
a ``root.after`` pump. ``call_on_main`` is a convenience wrapper that
runs the closure inline when already on the main thread (so synchronous
test calls don't need to drive the pump) and enqueues otherwise.

Usage::

    from update_queue import TkUpdateQueue

    queue = TkUpdateQueue(root)
    queue.start()

    # From any thread:
    queue.call_on_main(label.config, text="hello")

    # On shutdown:
    queue.stop()
"""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any, Callable

_log = logging.getLogger(__name__)


class TkUpdateQueue:
    """A thread-safe queue drained by ``root.after`` on the Tk main thread.

    The pump tick is 33 ms by default (~30 Hz), matching the Forza
    telemetry packet rate. Each tick drains every closure currently in
    the queue (bounded burst) so the queue cannot grow unbounded under
    backpressure.
    """

    def __init__(self, root, interval_ms: int = 33) -> None:
        self._root = root
        self._queue: queue.Queue = queue.Queue()
        self._interval = interval_ms
        self._pump_id: str | None = None
        self._stopped = False
        self._main_ident: int | None = None

    def enqueue(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Schedule ``fn(*args, **kwargs)`` to run on the Tk main thread.

        Safe to call from any thread.
        """
        if self._stopped:
            return
        self._queue.put((fn, args, kwargs))

    def call_on_main(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Run ``fn`` on the main thread.

        If the caller *is* the main thread (the one that called ``start``)
        the callback runs inline. Otherwise it is enqueued for the pump.
        ``start`` must have been called first; if it hasn't, the call is
        enqueued (deferred until ``start`` is invoked).
        """
        if self._main_ident is not None and threading.get_ident() == self._main_ident:
            try:
                fn(*args, **kwargs)
            except Exception:
                _log.exception("TkUpdateQueue main-thread callback raised")
            return
        self.enqueue(fn, *args, **kwargs)

    def start(self) -> None:
        """Begin pumping the queue. Must be called from the Tk main thread."""
        self._stopped = False
        self._main_ident = threading.get_ident()
        self._schedule()

    def stop(self) -> None:
        """Cancel the next pump tick. Pending items are discarded."""
        self._stopped = True
        if self._pump_id is not None:
            try:
                self._root.after_cancel(self._pump_id)
            except Exception:
                pass
            self._pump_id = None

    def pending(self) -> int:
        """Approximate number of queued closures. For tests/diagnostics."""
        return self._queue.qsize()

    def pump_once(self) -> int:
        """Drain everything currently in the queue once and return the count.

        Public for tests; the real pump tick uses this internally.
        """
        count = 0
        while True:
            try:
                fn, args, kwargs = self._queue.get_nowait()
            except queue.Empty:
                break
            try:
                fn(*args, **kwargs)
            except Exception:
                # An update callback failing should never tear down the pump.
                _log.exception("TkUpdateQueue callback raised")
            count += 1
        return count

    def _schedule(self) -> None:
        if self._stopped:
            return
        self._pump_id = self._root.after(self._interval, self._tick)

    def _tick(self) -> None:
        if self._stopped:
            return
        self.pump_once()
        self._schedule()
