"""Tests for the EXP farming mode (__exp_farming_setup).

Farming mode resets the car when stuck and presses brake to avoid AFK
detection. These tests verify the trigger conditions and cooldown timers.
"""

from __future__ import annotations

import sys
import os
import time
import types
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants
import keyboard_helper
from forza import Forza


def _make_forza_farming():
    """Create a Forza instance with farming enabled."""
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="test")
    f = Forza(pool, packet_format=constants.packet_format)
    f.farming = True
    f.reset_car = 0
    f.reset_time = time.time() - 20  # 20s ago so cooldown is elapsed
    f.break_timer = time.time() - 40  # 40s ago so brake timer is elapsed
    return f


def _make_fdp(**overrides):
    defaults = dict(
        car_ordinal=12345,
        norm_driving_line=0,
        speed=50.0,
        norm_ai_brake_diff=0,
    )
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


def test_reset_car_triggers_when_stuck_long_enough(monkeypatch):
    """Car reset fires after 100+ iterations off-track with 10s cooldown."""
    f = _make_forza_farming()
    f.reset_car = 100  # already at threshold

    reset_called = []
    monkeypatch.setattr(keyboard_helper, 'resetcar', lambda fz: reset_called.append(True))

    fdp = _make_fdp(norm_driving_line=127, speed=10)
    # Access private method
    f._Forza__exp_farming_setup(fdp)

    assert len(reset_called) == 1, "Should reset car when stuck for 100+ iterations"
    assert f.reset_car == 0, "Counter should be reset after triggering"


def test_reset_car_blocked_by_cooldown(monkeypatch):
    """Car reset doesn't fire if 10s cooldown hasn't elapsed."""
    f = _make_forza_farming()
    f.reset_car = 100
    f.reset_time = time.time()  # just reset, cooldown not elapsed

    reset_called = []
    monkeypatch.setattr(keyboard_helper, 'resetcar', lambda fz: reset_called.append(True))

    fdp = _make_fdp(norm_driving_line=127, speed=10)
    f._Forza__exp_farming_setup(fdp)

    assert len(reset_called) == 0, "Should not reset within 10s cooldown"
    assert f.reset_car == 101  # counter still increments


def test_reset_car_counter_resets_when_back_on_track():
    """Counter resets to 0 when car returns to normal driving line."""
    f = _make_forza_farming()
    f.reset_car = 50

    fdp = _make_fdp(norm_driving_line=50, speed=80)  # on track
    f._Forza__exp_farming_setup(fdp)

    assert f.reset_car == 0


def test_brake_press_fires_after_interval(monkeypatch):
    """Brake is pressed every 30s to avoid AFK detection."""
    f = _make_forza_farming()

    brake_called = []
    monkeypatch.setattr(keyboard_helper, 'press_brake', lambda fz: brake_called.append(True))

    fdp = _make_fdp(norm_ai_brake_diff=1)  # > 0 required
    f._Forza__exp_farming_setup(fdp)

    assert len(brake_called) == 1


def test_brake_press_blocked_within_interval(monkeypatch):
    """Brake is NOT pressed if less than 30s since last press."""
    f = _make_forza_farming()
    f.break_timer = time.time()  # just pressed

    brake_called = []
    monkeypatch.setattr(keyboard_helper, 'press_brake', lambda fz: brake_called.append(True))

    fdp = _make_fdp(norm_ai_brake_diff=1)
    f._Forza__exp_farming_setup(fdp)

    assert len(brake_called) == 0


def test_farming_skipped_when_disabled():
    """No farming logic runs when farming=False."""
    f = _make_forza_farming()
    f.farming = False
    f.reset_car = 200

    fdp = _make_fdp(norm_driving_line=127, speed=10)
    f._Forza__exp_farming_setup(fdp)

    # Counter should not change if farming is disabled
    assert f.reset_car == 200


def test_farming_skipped_when_no_car():
    """No farming logic runs when car_ordinal <= 0 (not in a car)."""
    f = _make_forza_farming()
    f.reset_car = 200

    fdp = _make_fdp(car_ordinal=0, norm_driving_line=127, speed=10)
    f._Forza__exp_farming_setup(fdp)

    assert f.reset_car == 200
