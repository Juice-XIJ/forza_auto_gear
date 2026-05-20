"""Small reusable GUI widgets and lifecycle helpers extracted from ``gui.py``.

Keeping these in their own module shrinks ``gui.py`` and makes the
utilities trivially testable in isolation.

Contents:

* :func:`round_rectangle` — draws a rounded rectangle as a polygon on a
  ``tkinter.Canvas``. Standalone (no longer an instance method).
* :func:`shutdown` — tears down the Forza UDP loop, the pynput listener,
  and the worker thread pool in the correct order.
"""

from __future__ import annotations

import tkinter
from concurrent.futures import ThreadPoolExecutor

from pynput.keyboard import Listener


def round_rectangle(canvas: tkinter.Canvas, x1, y1, x2, y2, radius: int = 25, **kwargs):
    """Draw a rectangle with rounded corners as a smoothed polygon.

    Args:
        canvas: target ``tkinter.Canvas``.
        x1, y1: top-left coordinates.
        x2, y2: bottom-right coordinates.
        radius: corner radius in pixels.
        **kwargs: forwarded to :py:meth:`tkinter.Canvas.create_polygon`.

    Returns:
        The integer item id of the created polygon.
    """
    points = [
        x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2,
        x1 + radius, y2, x1 + radius, y2, x1, y2,
        x1, y2 - radius, x1, y2 - radius, x1, y1 + radius,
        x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def shutdown(forza, threadPool: ThreadPoolExecutor, listener: Listener) -> None:
    """Tear down resources in an order that avoids races.

    1. Signal the Forza UDP loop to exit (so worker threads can return).
    2. Stop the pynput listener (so no new hotkey events arrive) and
       briefly join its thread so we don't leak a half-stopped global
       keyboard hook into the next phase (e.g. ``pause_handler`` rebuilds
       a fresh ``Listener``).
    3. Shut down the thread pool without blocking the caller; in-flight
       workers will observe ``isRunning == False`` and exit promptly.
    """
    forza.isRunning = False
    try:
        listener.stop()
        if hasattr(listener, "join"):
            try:
                listener.join(timeout=0.1)
            except RuntimeError:
                pass
    except Exception:
        pass
    threadPool.shutdown(wait=False)
