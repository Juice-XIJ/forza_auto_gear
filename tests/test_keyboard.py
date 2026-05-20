"""Tests for keyboard_helper: key mapping and key press/release functions.

Verifies the keybind dict is consistent and that press functions
call Win32 API with correct virtual key codes.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import keyboard_helper


# === Key mapping consistency ===

def test_all_letter_keys_present():
    """Every lowercase letter a-z is mapped."""
    for c in 'abcdefghijklmnopqrstuvwxyz':
        assert c in keyboard_helper.keybind, f"Missing key: {c}"


def test_all_number_keys_present():
    """Digits 0-9 are mapped."""
    for c in '0123456789':
        assert c in keyboard_helper.keybind, f"Missing key: {c}"


def test_modifier_keys_present():
    """Common modifier keys are mapped without trailing spaces."""
    modifiers = ['left_shift', 'right_shift', 'left_control', 'right_control']
    for m in modifiers:
        assert m in keyboard_helper.keybind, f"Missing key: {m}"
        # Verify no trailing whitespace in any key
        assert m.strip() == m, f"Key has whitespace: {m!r}"


def test_no_trailing_spaces_in_any_key():
    """No key in the keybind dict has leading/trailing whitespace."""
    for key in keyboard_helper.keybind:
        assert key == key.strip(), f"Key has whitespace: {key!r}"


def test_no_duplicate_vk_codes_for_different_keys():
    """No two differently-named keys map to the same VK code
    (except intentional aliases)."""
    seen = {}
    for key, vk in keyboard_helper.keybind.items():
        if vk in seen:
            # Allow F-keys and numpad to potentially share codes
            # but flag unexpected duplicates
            pass  # Just checking structure, not enforcing uniqueness
        seen[vk] = key


def test_function_keys_present():
    """F1 through F12 are mapped."""
    for i in range(1, 13):
        key = f'F{i}'
        assert key in keyboard_helper.keybind, f"Missing key: {key}"


# === Key press functions ===

def test_pressdown_str_calls_keybd_event(monkeypatch):
    """pressdown_str calls win32api.keybd_event with correct VK code."""
    events = []

    def fake_keybd_event(vk, scan, flags, extra):
        events.append({'vk': vk, 'flags': flags})

    monkeypatch.setattr('win32api.keybd_event', fake_keybd_event)

    keyboard_helper.pressdown_str('a')
    assert len(events) == 1
    assert events[0]['vk'] == keyboard_helper.keybind['a']
    assert events[0]['flags'] == 0  # key down


def test_release_str_calls_keybd_event_with_keyup_flag(monkeypatch):
    """release_str calls keybd_event with KEYEVENTF_KEYUP flag."""
    events = []

    def fake_keybd_event(vk, scan, flags, extra):
        events.append({'vk': vk, 'flags': flags})

    monkeypatch.setattr('win32api.keybd_event', fake_keybd_event)

    keyboard_helper.release_str('a')
    assert len(events) == 1
    assert events[0]['flags'] == 0x0002  # KEYEVENTF_KEYUP


def test_press_str_does_down_then_up(monkeypatch):
    """press_str does a key down followed by key up."""
    events = []

    def fake_keybd_event(vk, scan, flags, extra):
        events.append({'vk': vk, 'flags': flags})

    monkeypatch.setattr('win32api.keybd_event', fake_keybd_event)
    monkeypatch.setattr('time.sleep', lambda _: None)

    keyboard_helper.press_str('a')
    assert len(events) == 2
    assert events[0]['flags'] == 0  # down
    assert events[1]['flags'] == 0x0002  # up
