import ctypes
import time

import win32api
import win32con

keybind = {
    'q':81,
    'e':69,
    'i':73,
    'w': 87,
}

def pressdown_str(keystr):
    MapKey = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(keybind[keystr], MapKey(keybind[keystr], 0), 0, 0)

def pressup_str(keystr):
    MapKey = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(keybind[keystr], MapKey(keybind[keystr], 0), win32con.KEYEVENTF_KEYUP, 0)

def press_str(keystr):
    MapKey = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(keybind[keystr], MapKey(keybind[keystr], 0), 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(keybind[keystr], MapKey(keybind[keystr], 0), win32con.KEYEVENTF_KEYUP, 0)

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
