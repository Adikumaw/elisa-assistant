from pynput.keyboard import Controller
import time

keyboard = Controller()

time.sleep(2)  # Wait for 2 seconds before typing
keyboard.type("Hello, this is a test!")
