# This script plays an alarm sound effect when your mouse has been moved.
# Budget security system for protecting your base from robbers.
# Just attach a string to your mouse and your door, and that acts as a tripwire.
# Don't forget to download Alarm sound effect.mp3

# Requiresments:
# pynput
# soundfile
# sounddevice

from pynput import mouse
import sounddevice as sd
import soundfile as sf
import threading
import time

ALARM_ONCE = False

def play_alarm():
    while True:
        file_path = "Alarm sound effect.mp3"
        data, fs = sf.read(file_path)
        sd.play(data, fs)
        sd.wait()

        if ALARM_ONCE:
            break

def main():
    mouse_controller = mouse.Controller()
    saved_position = mouse_controller.position

    while True:
        if not mouse_controller.position == saved_position:
            break

        time.sleep(0.05)

    if ALARM_ONCE:
        play_alarm()
    else:
        threading.Thread(target=play_alarm, daemon=True).start()

        input("- Security system has been triggered. Press ENTER to stop the alarm. -")


if __name__ == "__main__":
    main()
