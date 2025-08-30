import keyboard
import time
import win32api, win32con
import pydirectinput
import threading

# ---------- Stop mechanism ----------
class StopMacro(Exception):
    pass

STOP_EVENT = threading.Event()

# Utility: precise wait loop
def wait_until(target_time):
    """Busy-wait until target_time (perf_counter). Abort if stop event is set."""
    while True:
        if STOP_EVENT.is_set():
            raise StopMacro()
        now = time.perf_counter()
        if now >= target_time:
            return
        time.sleep(0.001)  # sleep in small increments for accuracy


# ---------- Input helpers ----------
def move_mouse(x, y):
    win32api.mouse_event(
        win32con.MOUSEEVENTF_MOVE,
        int(x/1920*65535.0),
        int(y/1080*65535.0)
    )

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


# ---------- Macro (timestamp-driven) ----------
def run_macro():
    start_time = time.perf_counter()

    # List of (time offset in seconds, action)
    actions = [
        (0.00, lambda: keydown_w()),
        (1.1, lambda: keyup_w()),

        (1.07, lambda: move_mouse(22.5, 5)),
        (1.07, lambda: keydown_w()),
        (1.2, lambda: jump()), # 1 To start block

        (1.3, lambda: jump()), # 2 prejump
        (1.87, lambda: move_mouse(-28.2, 0)),
        
        (1.93, lambda: jump()), # 3 prejump 
        (2.952, lambda: move_mouse(20, 0)),
        
        (2.57, lambda: jump()), # 4 prejump

        (3.95, lambda: move_mouse(66.5, 0)),
        (4.07, lambda: jump()), # 5 big jump
        (4.53, lambda: move_mouse(18.25, 0)),
        (4.65, lambda: jump()), # 6

        (5.5, lambda: move_mouse(3.25, 0)),
        (5.66, lambda: jump()), # 7 Long jump

        (6.7, lambda: jump()), # 8

        (7.34, lambda: move_mouse(-54.6, 0)),
        (8.04, lambda: move_mouse(-47.5, 0)),
        (8.07, lambda: jump()), # 9 Corner jump

        (9.37, lambda: move_mouse(2.8, 0)),
        (9.47, lambda: jump()), # 10 Cross jump

        (10.27, lambda: move_mouse(7.45, 0)),
        (10.37, lambda: jump()), # 11 Block

        (11.35, lambda: jump()), # 12 Corner
        (11.55, lambda: move_mouse(35, 0)),
        (11.69, lambda: move_mouse(25, 0)),
        (12.11, lambda: move_mouse(15.8, 0)),
        (12.52, lambda: move_mouse(16.9, 0)),

        (12.8, lambda: jump()), # 13 End
        #(12.9, lambda: jump()), # 14 End*2

        (14, lambda: keyup_w()),

    ]

    try:
        for t_offset, action in actions:
            wait_until(start_time + t_offset)
            action()
    except StopMacro:
        pass
    finally:
        keyup_w()


# ---------- Runner ----------
def _run_macro_thread():
    STOP_EVENT.clear()
    run_macro()
    STOP_EVENT.clear()

def stop():
    STOP_EVENT.set()
    #keydown_w()
    keyup_w()


# Hotkeys
start_key = "x"
stop_key = "c"

keyboard.add_hotkey(start_key, lambda: threading.Thread(target=_run_macro_thread, daemon=True).start())
keyboard.add_hotkey(stop_key, stop)

print(f"Press '{start_key}' to start, '{stop_key}' to stop.")
keyboard.wait()