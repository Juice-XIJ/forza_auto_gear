"""End-to-end smoke test for MainWindow.

Constructs the window, drives all five hotkeys via ``on_press``, and
shuts down cleanly. This catches packaging/import regressions and basic
wiring breakage.
"""

from __future__ import annotations

import constants


def test_construct_destroy(main_window_factory):
    win = main_window_factory()
    win.root.update_idletasks()
    # If we reach this line, construction succeeded with all patches.
    assert hasattr(win, "ui_queue")
    assert hasattr(win, "threadPool")
    assert hasattr(win, "listener")
    assert hasattr(win, "forza5")


def test_all_hotkeys_dispatch_without_exception(main_window_factory, monkeypatch):
    win = main_window_factory()
    # Stub the heavy paths so we only test dispatch wiring.
    monkeypatch.setattr(win.forza5, "analyze", lambda **kw: None)
    monkeypatch.setattr(win.forza5, "test_gear", lambda *_a, **_k: None)
    monkeypatch.setattr(win.forza5, "run", lambda *_a, **_k: None)
    # Don't actually destroy the window inside the test; intercept exit.
    destroyed = {"flag": False}
    monkeypatch.setattr(win.root, "destroy", lambda: destroyed.__setitem__("flag", True))
    monkeypatch.setattr("helper.dump_settings", lambda *_a, **_k: None)

    for key in (
        constants.collect_data,
        constants.analysis,
        constants.auto_shift,
        constants.stop,
        # constants.close goes last because it stops the queue and destroys.
        constants.close,
    ):
        win.on_press(key)
        win.root.update_idletasks()

    assert destroyed["flag"], "End hotkey should have invoked destroy"


def test_update_car_info_via_queue_does_not_raise(main_window_factory, fake_fdp):
    win = main_window_factory()
    win.forza5.isRunning = True
    # _ui_update_car_info is the worker-safe shim; from a test thread it
    # runs inline, exercising the real update_car_info code path.
    win._ui_update_car_info(fake_fdp)
    win.root.update_idletasks()
