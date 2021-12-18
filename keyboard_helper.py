from concurrent.futures import ThreadPoolExecutor

import ctypes
import threading
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
    # time.sleep(0.001)

def pressup_str(keystr):
    key = keystr if keystr not in keybind else keybind[keystr]
    MapKey = ctypes.windll.user32.MapVirtualKeyA
    win32api.keybd_event(key, MapKey(key, 0), win32con.KEYEVENTF_KEYUP, 0)
    # time.sleep(0.001)

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

def get_thread_id(thread):
    for id, t in threading._active.items():
        if t is thread:
            return id

def raise_exception(thread_id):
    import ctypes
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                     ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        logger.info('Exception raise failure')

def stop(threadPool):
    for thread in threadPool._threads:
        id = get_thread_id(thread)
        raise_exception(id)

    threadPool.shutdown(wait=False)

def restart(threadPool):
    stop(threadPool)
    return ThreadPoolExecutor(max_workers=1, thread_name_prefix="exec")