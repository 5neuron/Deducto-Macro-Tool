import keyboard
import time
import win32api, win32con
import pydirectinput
import threading

# ---------- Stop mechanism ----------
class StopMacro(Exception):
    pass

STOP_EVENT = threading.Event()

FPS = 50
FRAME_TIME = 1.0 / FPS  # 20 ms per frame


# ---------- Input helpers ----------
def move_mouse(x, y):
    win32api.mouse_event(
        win32con.MOUSEEVENTF_MOVE,
        int(x/1920*65535.0),
        int(y/1080*65535.0)
    )

def press(key):
    pydirectinput.press(key)

def jump():
    pydirectinput.press('space')

def keydown_w():
    pydirectinput.keyDown('w')

def keyup_w():
    pydirectinput.keyUp('w')

{   ######################### SETTINGS #########################
                
    ######## START POS ########
    #    X       Y       Z    #
    #  -14.80  0.357  27.965  #
    ###########################

    # FPS:  50
    # SENS: 50
            
    # Degrees-to-Input Conversion Table (based on 35.1605 ≈ 90°)
    #  1°    ->  0.3907
    #  5°    ->  1.9534
    # 10°    ->  3.9067
    # 15°    ->  5.8601
    # 22.5°  ->  8.7896
    # 30°    -> 11.7202
    # 45°    -> 17.5803
    # 60°    -> 23.4403
    # 75°    -> 29.3004
    # 90°    -> 35.1605
    # 120°   -> 46.8806
    # 135°   -> 52.7406
    # 180°   -> 70.3210
}

# ---------- Macro (frame-driven) ----------
def run_macro():
    # List of (frame, action)
    actions = [
        (1,   lambda: move_mouse(0, 5)), # better POV

        (5,   lambda: move_mouse(-0.557, 0)), # slight angle for late start

        (10,  lambda: keydown_w()),
        (25,  lambda: jump()),  # 1 - To start block

        (54,  lambda: move_mouse(0.557, 0)), # this should cancel out the first moveX, pretty sure this is the way to go
        (56,  lambda: move_mouse(11.43, 0)),
        (63,  lambda: jump()), # 2

        (94,  lambda: move_mouse(-11.43, 0)), # -moveX
        (95,  lambda: move_mouse(-17.1605, 0)),
        (95,  lambda: jump()), # 3

        (116, lambda: move_mouse(-10.7, 0)),

        # NOTE: sum(moveX) = -35.1605 (-90º) for perfect turn
        # ik rn its not but its cuz you cant get next jump before f121 anyway so u might as well go as far as possible

        # should be prejump, but it's bugged <3
        (121, lambda: move_mouse(30.15, 0)),
        (121, lambda: jump()), # 4 - "prejump"
        
        # FIXED PREJUMPS (for some reason the next prejumps work xD)
        (122, lambda: jump()), # 5 - prejump
        (155, lambda: move_mouse(32.72, 0)), # 1 frame "savable" here if you mess with the angles before this one
        
        (158, lambda: jump()), # 6 - prejump
        (194, lambda: move_mouse(21.43, 0)), # if you can overjump, aiming closer to wall is good too

        (228, lambda: move_mouse(11.3, 0)),
        (230, lambda: jump()), # 7

        (265, lambda: jump()), # 8 - onto mid
        (300, lambda: move_mouse(-14.9987, 0)),
        (302, lambda: move_mouse(-18, 0)), # 17.5803 = 45º
        # NOTE: sum(moveX) = -35.1605 (-90º) for perfect turn (its not rn)

        (334, lambda: move_mouse(-21.8, 0)), # 17.5803 = 45º
        (342, lambda: jump()), # 9 - f342 is inconsistent

        (342, lambda: move_mouse(0.1, 0)), # pre-move cuz there's a random delay here <3

        (371, lambda: move_mouse(-13.0408, 0)), # any sooner leads to time loss
        # NOTE: sum(moveX) = 0 (0º) for perfect turn

        (375, lambda: move_mouse(-20.69, 0)),
        (386, lambda: move_mouse(4.62, 0)),

        (401, lambda: move_mouse(10.63, 0)),
        (414, lambda: jump()), # 10
        
        #(438, lambda: move_mouse(5.43, 0)),
        # NOTE: sum(moveX) = 0 (0º) for perfect turn
        # -> -5.43
        (442, lambda: move_mouse(30.52, 0)),

        (464, lambda: move_mouse(-23.5, 0)), # aim for lower hitbox (50% success rate on -23.5; change to -23.51 if u want consistency)
        (464, lambda: jump()), # 11

        (465, lambda: jump()), # 12 - prejump, wall into ending
        (505, lambda: move_mouse(36.35, 0)),

        # ENDING LOWER SECTION:
        (521, lambda: move_mouse(7.65, 0)),

        (522, lambda: jump()), # 13 - prejump, first ending platform (this has to be here or it will give the next move a delay <3)
        (549, lambda: move_mouse(22.79, 0)), # you can land 22.80 but its super inconsistent, even 22.79 is tight

        (560, lambda: move_mouse(22.25, 5)),

        #(561, lambda: jump()), # 14 - prejump to last platform
        (588, lambda: move_mouse(-22.35, 0)),
        (588, lambda: jump()), # 14 - insta-jump to last platform
        #(590, lambda: move_mouse(-1, 0)),

        (616, lambda: move_mouse(-9.7, 0)),
        (623, lambda: jump()), # 16 - The Jump.


        #(700, lambda: keyup_w())
    ]

    # Convert to dict for efficient lookup
    frame_actions = {}
    for frame, action in actions:
        frame_actions.setdefault(frame, []).append(action)

    start_time = time.perf_counter()
    frame = 0

    try:
        while not STOP_EVENT.is_set():
            target_time = start_time + frame * FRAME_TIME
            now = time.perf_counter()

            while now < target_time:
                if STOP_EVENT.is_set():
                    raise StopMacro()
                time.sleep(0.0001)
                now = time.perf_counter()

            if frame in frame_actions:
                for action in frame_actions[frame]:
                    action()

            frame += 1

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
    keyup_w()


# Hotkeys
start_key = "x"
stop_key = "c"

keyboard.add_hotkey(start_key, lambda: threading.Thread(target=_run_macro_thread, daemon=True).start())
keyboard.add_hotkey(stop_key, stop)

print(f"Press '{start_key}' to start, '{stop_key}' to stop.")
keyboard.wait()
