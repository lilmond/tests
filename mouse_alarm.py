# This script plays an alarm sound effect when your mouse has been moved.
# Budget security system for protecting your base from robbers.
# Just attach a string to your mouse and your door.

# Requiresments:
# pynput
# soundfile
# sounddevice

from pynput import mouse
import sounddevice as sd
import soundfile as sf
import time

def main():
    mouse_controller = mouse.Controller()
    saved_position = mouse_controller.position

    while True:
        if not mouse_controller.position == saved_position:
            break

        time.sleep(0.05)

    file_path = "Alarm sound effect.mp3"
    data, fs = sf.read(file_path)
    sd.play(data, fs)
    sd.wait()

if __name__ == "__main__":
    main()
