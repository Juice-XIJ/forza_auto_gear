"""Tests for the shifting logic in Forza.shifting().

The shifting engine is the core feature — it reads telemetry (RPM, speed,
slip, gear, drivetrain) and decides whether to upshift, downshift, or hold.
These tests verify every decision branch using synthetic ForzaDataPacket data.
"""

from __future__ import annotations

import sys
import os
import types
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants
from forza import Forza


def _make_forza(**overrides):
    """Create a Forza instance with patched I/O for pure-logic testing."""
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="test")
    f = Forza(pool, packet_format=constants.packet_format)
    f.shift_point = {
        1: {'rpmo': 6000, 'speed': 60},
        2: {'rpmo': 6500, 'speed': 100},
        3: {'rpmo': 7000, 'speed': 140},
        4: {'rpmo': 7200, 'speed': 180},
    }
    f.minGear = 1
    f.maxGear = 5
    f.shift_point_factor = 1.0
    f.car_drivetrain = 0  # AWD by default
    for k, v in overrides.items():
        setattr(f, k, v)
    return f


def _make_fdp(**overrides):
    """Create a fake FDP with sensible defaults for shifting tests."""
    defaults = dict(
        gear=3,
        current_engine_rpm=5000,
        speed=30.0,  # m/s (108 km/h)
        accel=200,
        tire_slip_ratio_RL=0.1,
        tire_slip_ratio_RR=0.1,
        tire_slip_ratio_FL=0.1,
        tire_slip_ratio_FR=0.1,
        tire_slip_angle_RL=0.0,
        tire_slip_angle_RR=0.0,
        tire_slip_angle_FL=0.0,
        tire_slip_angle_FR=0.0,
    )
    defaults.update(overrides)

    fdp = types.SimpleNamespace(**defaults)
    fdp.to_list = lambda props: [getattr(fdp, p, None) for p in props]
    return fdp


# === Upshift tests ===

def test_upshift_triggers_when_rpm_and_speed_exceed_target():
    """Upshift fires when RPM > target AND speed > target AND slip < 1."""
    f = _make_forza()
    fdp = _make_fdp(gear=2, current_engine_rpm=7000, speed=30.0)  # 108 km/h > 100
    iteration = f.shifting(0, fdp)
    assert iteration == 1  # iteration increments = shifting ran


def test_upshift_blocked_when_rpm_below_target():
    """No upshift when RPM is below the shift point threshold."""
    import gear_helper
    f = _make_forza()
    # Patch gear_helper to detect if upshift was called
    called = []
    original = gear_helper.up_shift_handle
    gear_helper.up_shift_handle = lambda g, fz: called.append(g)
    try:
        fdp = _make_fdp(gear=2, current_engine_rpm=3000, speed=30.0)
        f.shifting(0, fdp)
        assert len(called) == 0, "Should not upshift when RPM below target"
    finally:
        gear_helper.up_shift_handle = original


def test_upshift_blocked_when_slip_high():
    """No upshift when rear tire slip >= 1."""
    import gear_helper
    f = _make_forza()
    called = []
    original = gear_helper.up_shift_handle
    gear_helper.up_shift_handle = lambda g, fz: called.append(g)
    try:
        fdp = _make_fdp(gear=2, current_engine_rpm=7000, speed=30.0,
                        tire_slip_ratio_RL=1.5, tire_slip_ratio_RR=1.5)
        f.shifting(0, fdp)
        assert len(called) == 0, "Should not upshift when slip >= 1"
    finally:
        gear_helper.up_shift_handle = original


def test_upshift_skipped_at_max_gear():
    """No upshift attempt when already at max gear."""
    import gear_helper
    f = _make_forza(maxGear=5)
    called = []
    original = gear_helper.up_shift_handle
    gear_helper.up_shift_handle = lambda g, fz: called.append(g)
    try:
        fdp = _make_fdp(gear=5, current_engine_rpm=8000, speed=60.0)
        f.shifting(0, fdp)
        assert len(called) == 0
    finally:
        gear_helper.up_shift_handle = original


# === Downshift tests ===

def test_downshift_triggers_when_speed_below_threshold():
    """Downshift fires when speed < 95% of lower gear target."""
    import gear_helper
    f = _make_forza()
    called = []
    original = gear_helper.down_shift_handle
    gear_helper.down_shift_handle = lambda g, fz: called.append(g)
    try:
        # Gear 3, target_down_speed for gear 2 = 100 km/h, 95% = 95 km/h
        # Speed = 20 km/h (5.5 m/s), well below threshold
        fdp = _make_fdp(gear=3, current_engine_rpm=3000, speed=5.5, accel=0)
        f.shifting(0, fdp)
        assert len(called) == 1, "Should downshift when speed far below target"
    finally:
        gear_helper.down_shift_handle = original


def test_downshift_blocked_when_speed_above_threshold():
    """No downshift when speed is above the lower gear target."""
    import gear_helper
    f = _make_forza()
    called = []
    original = gear_helper.down_shift_handle
    gear_helper.down_shift_handle = lambda g, fz: called.append(g)
    try:
        fdp = _make_fdp(gear=3, current_engine_rpm=5000, speed=40.0, accel=0)
        f.shifting(0, fdp)
        assert len(called) == 0
    finally:
        gear_helper.down_shift_handle = original


def test_downshift_skipped_at_min_gear():
    """No downshift when already at min gear."""
    import gear_helper
    f = _make_forza(minGear=1)
    called = []
    original = gear_helper.down_shift_handle
    gear_helper.down_shift_handle = lambda g, fz: called.append(g)
    try:
        fdp = _make_fdp(gear=1, current_engine_rpm=2000, speed=2.0, accel=0)
        f.shifting(0, fdp)
        assert len(called) == 0
    finally:
        gear_helper.down_shift_handle = original


# === RWD-specific tests ===

def test_rwd_uses_same_threshold_as_awd():
    """RWD currently uses the same upshift thresholds as AWD/FWD."""
    import gear_helper
    f = _make_forza(car_drivetrain=1)  # RWD
    called = []
    original = gear_helper.up_shift_handle
    gear_helper.up_shift_handle = lambda g, fz: called.append(g)
    try:
        # Gear 2, shift_point[2] = rpmo:6500, speed:100
        # RPM 7000 > 6500 ✓, speed 30.0 m/s = 108 km/h > 100 ✓, slip < 1 ✓
        fdp = _make_fdp(gear=2, current_engine_rpm=7000, speed=30.0)
        f.shifting(0, fdp)
        assert len(called) == 1, "RWD should upshift with same thresholds as AWD"
    finally:
        gear_helper.up_shift_handle = original


def test_rwd_high_gear_uses_normal_threshold():
    """RWD at gear >= 3 uses normal thresholds (no 0.95 factor)."""
    import gear_helper
    f = _make_forza(car_drivetrain=1)  # RWD
    called = []
    original = gear_helper.up_shift_handle
    gear_helper.up_shift_handle = lambda g, fz: called.append(g)
    try:
        # Gear 3, shift_point[3] = rpmo:7000, speed:140
        # Normal threshold: rpm > 7000, speed > 140
        # RPM 7100 > 7000 ✓, speed 40.0 m/s = 144 km/h > 140 ✓
        fdp = _make_fdp(gear=3, current_engine_rpm=7100, speed=40.0)
        f.shifting(0, fdp)
        assert len(called) == 1
    finally:
        gear_helper.up_shift_handle = original


def test_rwd_no_downshift_to_gear_1():
    """RWD doesn't downshift when current gear < 3 (protects against gear 1)."""
    import gear_helper
    f = _make_forza(car_drivetrain=1, minGear=1)
    called = []
    original = gear_helper.down_shift_handle
    gear_helper.down_shift_handle = lambda g, fz: called.append(g)
    try:
        fdp = _make_fdp(gear=2, current_engine_rpm=2000, speed=2.0, accel=0)
        f.shifting(0, fdp)
        assert len(called) == 0, "RWD should not downshift from gear 2 to gear 1"
    finally:
        gear_helper.down_shift_handle = original


# === Edge cases ===

def test_no_shift_when_stationary():
    """No shifting decisions when car speed <= 0.1 m/s."""
    f = _make_forza()
    fdp = _make_fdp(speed=0.0)
    result = f.shifting(0, fdp)
    assert result == 0, "Iteration should not increment for stationary car"


def test_no_shift_when_no_shift_points():
    """No shifting when shift_point is empty (no config loaded)."""
    f = _make_forza()
    f.shift_point = {}
    fdp = _make_fdp(gear=3, current_engine_rpm=8000, speed=50.0)
    result = f.shifting(0, fdp)
    assert result == 0


def test_no_shift_when_not_accelerating():
    """Upshift should not fire when not accelerating (accel=0)."""
    import gear_helper
    f = _make_forza()
    called = []
    original = gear_helper.up_shift_handle
    gear_helper.up_shift_handle = lambda g, fz: called.append(g)
    try:
        fdp = _make_fdp(gear=2, current_engine_rpm=7000, speed=30.0, accel=0)
        f.shifting(0, fdp)
        assert len(called) == 0, "Should not upshift when not accelerating"
    finally:
        gear_helper.up_shift_handle = original
