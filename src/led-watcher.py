import random
import time
import traceback
from RPi import GPIO

BTN = 12
PIN_BY_LED_COLOR = dict(
    red = 11,
    yellow = 13,
    blue = 15,
)
POLLING_INTERVAL = 0.5


def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BTN, GPIO.IN, GPIO.PUD_DOWN)
    for pin in PIN_BY_LED_COLOR.values():
        GPIO.setup(pin, GPIO.OUT)

    GPIO.add_event_detect(
        BTN, GPIO.RISING, callback=on_button_pressed, bouncetime=200
    )


def on_button_pressed(_):
    for pin in PIN_BY_LED_COLOR.values():
        GPIO.output(pin, False)


def has_error():
    return random.random() > 0.95


def has_warning():
    return random.random() > 0.95


def time_to_forage():
    return random.random() > 0.95


def check_status():
    state_by_color = {
        'red': has_error(),
        'yellow': has_warning(),
        'blue': time_to_forage(),
    }

    for color, state in state_by_color.items():
        if state:
            GPIO.output(PIN_BY_LED_COLOR[color], True)


def loop():
    try:
        while True:
            check_status()
            time.sleep(POLLING_INTERVAL)
    except:
        traceback.print_exc()
        GPIO.cleanup()

init()
loop()
