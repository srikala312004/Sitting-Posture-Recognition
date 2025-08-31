import cv2
import math
import time
import numpy as np
import threading
import tkinter as tk
from config_reader import config_reader
from scipy.ndimage.filters import gaussian_filter 
from model import get_testing_model

# ========================
# GLOBAL VARIABLES
# ========================
last_tick = time.time()
good_seconds = 0
bad_seconds = 0
posture_points = 0

bad_posture_start = None
no_person_start = None

BAD_POSTURE_LIMIT_SEC = 5
NO_PERSON_LIMIT_SEC = 5
SCORE_GOOD_SEC = 2
SCORE_BAD_SEC = -1

# ========================
# POPUP CLASS
# ========================
class StatusPopup(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.root = None
        self.label = None

    def run(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry("200x50+50+50")
        self.label = tk.Label(self.root, text="", font=("Helvetica", 14))
        self.label.pack(fill="both", expand=True)
        self.root.mainloop()

    def show(self, text, color):
        if self.label:
            self.label.config(text=text, bg=color)

# ========================
# DUMMY HELPERS (replace with your actual ones)
# ========================
def process(frame, params, model_params):
    # TODO: Put your pose detection here
    # For now, just simulate posture
    import random
    posture = random.choice(["GOOD", "BAD", "NOPERSON"])
    return frame, posture

def beep():
    print("BEEP!")

def speak(msg):
    print("VOICE:", msg)

# ========================
# MAIN
# ========================
if __name__ == '__main__':
    popup = StatusPopup()
    popup.start()

    print('Start processing...')
    model = get_testing_model()
    model.load_weights('./model/keras/model.h5')

    cap = cv2.VideoCapture(0)
    vi = cap.isOpened()

    if vi:
        cap.set(100, 160)
        cap.set(200, 120)
        time.sleep(2)

        last_score_update = time.time()
        start_time = time.time()
        DURATION = 20   # run only 20 seconds

        # Initialize timer
        last_tick = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                popup.show("Camera Error", "gray")
                break

            params, model_params = config_reader()
            canvas, posture = process(frame, params, model_params)

            now = time.time()
            dt = now - last_tick
            last_tick = now

            # ================= Status Indicator =================
            if posture == "GOOD":
                popup.show("Good Posture", "green")
            elif posture == "BAD":
                popup.show("Bad Posture", "red")
            else:
                popup.show("No Person", "gray")

            # ================= Alerts =================
            if posture == "BAD":
                if bad_posture_start is None:
                    bad_posture_start = now
                if (now - bad_posture_start) >= BAD_POSTURE_LIMIT_SEC:
                    threading.Thread(target=beep, daemon=True).start()
                    speak("Please sit up straight")
                    bad_posture_start = now
                no_person_start = None

            elif posture == "GOOD":
                bad_posture_start = None
                no_person_start = None

            elif posture == "NOPERSON":
                if no_person_start is None:
                    no_person_start = now
                if (now - no_person_start) >= NO_PERSON_LIMIT_SEC:
                    speak("Please sit in view of the camera")
                    no_person_start = now
                bad_posture_start = None

            # ================= Scoring =================
            if posture == "GOOD":
                good_seconds += dt
                posture_points += SCORE_GOOD_SEC * int(dt)
            elif posture == "BAD":
                bad_seconds += dt
                posture_points += SCORE_BAD_SEC * int(dt)

            # ================= HUD Overlay =================
            hud = f"Status: {posture} | Good(min): {int(good_seconds/60)} | Bad(min): {int(bad_seconds/60)} | Points: {posture_points}"
            cv2.putText(canvas, hud, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                        (0, 255, 0) if posture == "GOOD" else (0, 0, 255), 2)

            cv2.imshow("Posture Assistant", canvas)

            # Stop after 20 sec
            if now - start_time >= DURATION:
                print("\n=== 20-Second Briefing ===")
                print(f"Good Sitting Time: {int(good_seconds)} sec")
                print(f"Bad Sitting Time : {int(bad_seconds)} sec")
                print(f"Total Points     : {posture_points}")
                print("==========================\n")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


