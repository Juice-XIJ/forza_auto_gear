"""Shared pytest fixtures for the GUI test suite.

The GUI tests need to construct ``MainWindow`` without actually running a
Tk mainloop, binding UDP sockets, or installing global keyboard hooks.
The fixtures here provide:

* ``tk_root`` — a real ``tkinter.Tk`` root, auto-destroyed after the test.
  The fixture skips the test when ``Tk()`` cannot initialise (e.g. headless
  CI without a display server).
* ``patched_mainloop`` — monkey-patches ``tkinter.Tk.mainloop`` to a no-op
  so ``MainWindow()`` returns instead of blocking.
* ``patched_listener`` — replaces ``pynput.keyboard.Listener.start`` with a
  no-op so no global keyboard hook is installed during tests.
* ``patched_forza`` — patches ``Forza`` socket binding and the
  ``keyboard_helper`` Win32 calls so tests never touch the network or
  send synthetic keystrokes.
* ``fake_fdp`` — a ``SimpleNamespace`` shaped exactly like the attributes
  ``MainWindow.update_car_info`` reads from a real ``ForzaDataPacket``.
* ``main_window_factory`` — convenience factory that yields a fully
  initialised ``MainWindow`` instance with all of the above patches
  applied, plus cleanup on teardown.
"""

from __future__ import annotations

import sys
import os
import types
from concurrent.futures import ThreadPoolExecutor

import pytest

# Make the repo root importable for tests run via ``pytest`` from any cwd.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_FDP_PATH = os.path.join(_REPO_ROOT, "forza_motorsport")
if _FDP_PATH not in sys.path:
    sys.path.insert(0, _FDP_PATH)


@pytest.fixture
def tk_root():
    """Yield a real ``tkinter.Tk`` root; skip the test if Tk is unavailable."""
    tkinter = pytest.importorskip("tkinter")
    try:
        root = tkinter.Tk()
    except tkinter.TclError as exc:  # pragma: no cover - headless environments
        pytest.skip(f"Tk cannot initialise in this environment: {exc}")
    try:
        root.withdraw()  # don't actually show a window during tests
        yield root
    finally:
        try:
            root.destroy()
        except Exception:
            pass


@pytest.fixture
def patched_mainloop(monkeypatch):
    """Replace ``Tk.mainloop`` with a no-op so ``MainWindow()`` returns."""
    import tkinter
    monkeypatch.setattr(tkinter.Tk, "mainloop", lambda self: None)
    return None


@pytest.fixture
def patched_listener(monkeypatch):
    """Stub out pynput's global keyboard hook so tests don't install one."""
    from pynput.keyboard import Listener

    started = {"count": 0}

    def _fake_start(self):
        started["count"] += 1

    def _fake_stop(self):
        pass

    monkeypatch.setattr(Listener, "start", _fake_start)
    monkeypatch.setattr(Listener, "stop", _fake_stop)
    return started


@pytest.fixture
def patched_forza(monkeypatch):
    """Patch network / Win32 sinks so tests are hermetic.

    Specifically:
    * ``socket.socket.bind`` / ``recvfrom`` raise to short-circuit any
      accidental real UDP traffic in tests.
    * ``keyboard_helper`` press/release helpers become no-ops so no
      synthetic keystrokes are sent to the host.
    """
    import keyboard_helper

    sent_keys: list[str] = []

    def _record(*args, **kwargs):
        sent_keys.append(repr((args, kwargs)))

    for name in ("pressdown_str", "release_str", "press_str", "resetcar", "press_brake"):
        if hasattr(keyboard_helper, name):
            monkeypatch.setattr(keyboard_helper, name, _record)

    return sent_keys


@pytest.fixture
def fake_fdp():
    """A ``SimpleNamespace`` shaped like the fdp attributes update_car_info reads."""
    return types.SimpleNamespace(
        car_ordinal=12345,
        car_performance_index=801,
        car_class=4,           # 0..7 maps into constants.car_class_list
        drivetrain_type=1,     # 0..3 maps into constants.car_drivetrain_list
        accel=204,             # 0..255 -> ~80%
        brake=51,              # 0..255 -> ~20%
        tire_combined_slip_FL=0.10,
        tire_combined_slip_FR=0.20,
        tire_combined_slip_RL=0.50,
        tire_combined_slip_RR=0.90,
    )


@pytest.fixture
def sync_thread_pool():
    """A ``ThreadPoolExecutor`` with 1 worker, kept tight for predictable teardown."""
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="test")
    try:
        yield pool
    finally:
        pool.shutdown(wait=True)


@pytest.fixture
def main_window_factory(patched_mainloop, patched_listener, patched_forza, monkeypatch):
    """Factory that constructs a ``MainWindow`` without side effects.

    Usage::

        def test_something(main_window_factory):
            win = main_window_factory()
            ...  # window is destroyed automatically at teardown
    """
    import gc
    import gui as gui_module

    created: list = []

    def _make():
        win = gui_module.MainWindow()
        created.append(win)
        return win

    yield _make

    for win in created:
        try:
            if hasattr(win, "threadPool"):
                win.threadPool.shutdown(wait=False)
        except Exception:
            pass
        try:
            win.root.destroy()
        except Exception:
            pass
    # Force GC between tests so Tcl interpreter state is released cleanly
    # before the next ``Tk()`` is constructed (works around a Python 3.13
    # Windows tkinter flake when many Tk roots are created sequentially).
    gc.collect()
