import keyboard
import time
import win32api, win32con
import pydirectinput
import threading

class StopMacro(Exception):
    pass

STOP_EVENT = threading.Event()

# Precise wait stuff
def wait_until(target_time):
    while True:
        if STOP_EVENT.is_set():
            raise StopMacro()
        now = time.perf_counter()
        if now >= target_time:
            return
        time.sleep(0.001)  # sleep in small increments for accuracy

def move_mouse(x, y):
    win32api.mouse_event(
        win32con.MOUSEEVENTF_MOVE,
        int(x/1920*65535.0),
        int(y/1080*65535.0))

def move(key, duration):
    pydirectinput.keyDown(key)
    time.sleep(duration)
    pydirectinput.keyUp(key)

def press(key):
    pydirectinput.press(key)

def jump():
    pydirectinput.press('space')

def keydown_w():
    pydirectinput.keyDown('w')

def keyup_w():
    pydirectinput.keyUp('w')


def run_macro():
    start_time = time.perf_counter()

    # List of macro actions
    actions = [
        #Example. First number means at what time should the macro be performed, for example, (0.00, lambda: keydown_w()) means at 0.00 seconds, perform keydown_() function (hold w down).
        (0.00, lambda: keydown_w()),
        (1.00, lambda: keyup_w()),
        (1.00, lambda: move_mouse(22, 5)), # means move mouse 22 in the x axis and move 5 in the y axis 
        (1.00, lambda: keydown_w()),
        (1.20, lambda: jump()), # perform the jump function, typically associated with pressing space in-game.
        (1.50, lambda: keyup_w()) 
        ]

    try:
        for t_offset, action in actions:
            wait_until(start_time + t_offset)
            action()
    except StopMacro:
        pass
    finally:
        keyup_w()

def _run_macro_thread():
    STOP_EVENT.clear()
    run_macro()
    STOP_EVENT.clear()

def stop():
    STOP_EVENT.set()
    keyup_w()

# Hotkeys
start_key = "x"
stop_key = "c"

keyboard.add_hotkey(start_key, lambda: threading.Thread(target=_run_macro_thread, daemon=True).start())
keyboard.add_hotkey(stop_key, stop)

print(f"Press '{start_key}' to start, '{stop_key}' to stop.")
keyboard.wait()