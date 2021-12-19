import ctypes
import time

import win32api
import win32con

from logger import logger

keycooldown = 0.0001

LEFT = 37
UP = 38
RIGHT = 39
DOWN = 40
ENTER = 13

LEFT = 65
DOWN = 83
UP = 87
RIGHT = 68

keybind = {
    "up": UP,
    "left": LEFT,
    "down": DOWN,
    "right": RIGHT,
    'enter': ENTER,
    "esc": 27,
    'tab':9,
    'q':81,
    'e':69,
    'i':73,
    'shift':16,
    'w': 87,
}

def pressdown_str(keystr):
    key = keystr if keystr not in keybind else keybind[keystr]
    MapKey = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(key, MapKey(key, 0), 0, 0)

def pressup_str(keystr):
    key = keystr if keystr not in keybind else keybind[keystr]
    MapKey = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(key, MapKey(key, 0), win32con.KEYEVENTF_KEYUP, 0)

def press_str(keystr):
    key = keystr if keystr not in keybind else keybind[keystr]
    MapKey = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(key, MapKey(key, 0), 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(key, MapKey(key, 0), win32con.KEYEVENTF_KEYUP, 0)

def get_key_name(key):
    t = None
    try:
        t = key.char
    except:
        try:
            t = key.name
        except:
            return ""
    return t
