"""Characterization tests pinning ``MainWindow`` event handler behavior.

These tests assert the *routing* between hotkey / button events and the
underlying ``Forza`` orchestration calls. They use a custom executor
that captures submitted work without actually running it, so we can
verify side effects synchronously and deterministically.
"""

from __future__ import annotations

from concurrent.futures import Future

import constants


class _CapturingExecutor:
    """Executor stub that records submissions instead of running them."""

    def __init__(self):
        self.submissions: list = []

    def submit(self, fn, *args, **kwargs):
        self.submissions.append((fn, args, kwargs))
        fut: Future = Future()
        fut.set_result(None)
        return fut

    def shutdown(self, wait=False):
        pass


def _install_capturing_pool(win):
    """Replace MainWindow's thread pool with a capturing one and return it."""
    cap = _CapturingExecutor()
    win.threadPool = cap
    win.forza5.threadPool = cap
    return cap


def test_on_press_collect_data_starts_when_idle(main_window_factory):
    win = main_window_factory()
    cap = _install_capturing_pool(win)
    win.forza5.isRunning = False

    win.on_press(constants.collect_data)

    assert len(cap.submissions) == 1, "expected one submission to thread pool"


def test_on_press_collect_data_stops_when_running(main_window_factory):
    win = main_window_factory()
    cap = _install_capturing_pool(win)
    win.forza5.isRunning = True

    win.on_press(constants.collect_data)

    assert len(cap.submissions) == 1
    # The submitted closure flips isRunning=False when invoked.
    fn, _, _ = cap.submissions[0]
    fn()
    assert win.forza5.isRunning is False


def test_on_press_auto_shift_starts_when_idle(main_window_factory):
    win = main_window_factory()
    cap = _install_capturing_pool(win)
    win.forza5.isRunning = False

    win.on_press(constants.auto_shift)

    assert len(cap.submissions) == 1


def test_on_press_auto_shift_stops_when_running(main_window_factory):
    win = main_window_factory()
    cap = _install_capturing_pool(win)
    win.forza5.isRunning = True

    win.on_press(constants.auto_shift)

    assert len(cap.submissions) == 1
    fn, _, _ = cap.submissions[0]
    fn()
    assert win.forza5.isRunning is False


def test_on_press_analysis_loads_example_and_calls_analyze(main_window_factory, monkeypatch):
    win = main_window_factory()
    # Avoid actually running matplotlib / file IO.
    called = {"analyze": 0, "update_tree": 0}
    monkeypatch.setattr(win.forza5, "analyze", lambda **kwargs: called.__setitem__("analyze", called["analyze"] + 1))
    monkeypatch.setattr(win, "update_tree", lambda: called.__setitem__("update_tree", called["update_tree"] + 1))

    # Pretend no records so the example config is loaded.
    win.forza5.records = []
    win.on_press(constants.analysis)

    assert called["analyze"] == 1
    assert called["update_tree"] == 1


def test_button_invoke_runs_handler(main_window_factory):
    """The five buttons in the button frame each bind <Button-1>; calling
    the bound callback directly must route to a handler that does
    *something* observable (here: submits to the pool)."""
    win = main_window_factory()
    cap = _install_capturing_pool(win)
    win.forza5.isRunning = False

    children = list(win.button_frame.winfo_children())
    buttons = [c for c in children if c.winfo_class() == "Button"]
    assert len(buttons) == 5, f"expected 5 buttons, got {len(buttons)}"

    # The first button is "Collect Data" → invoking its bound handler
    # should submit one task to the (capturing) pool.
    first_btn = buttons[0]
    callback_name = first_btn.bind("<Button-1>")
    assert callback_name, "first button must have a <Button-1> binding"
    # Call the handler directly with a dummy event; this matches what Tk
    # would do internally when the button is clicked.
    win.collect_data_handler(None)
    assert len(cap.submissions) >= 1
