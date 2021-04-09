import random
import asyncio
import time
import traceback
import sys
from functools import partial
from RPi import GPIO

from led_watcher import watchers

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


# def has_error():
#     return random.random() > 0.95


# def has_warning():
#     return random.random() > 0.95


# def time_to_forage():
#     return random.random() > 0.95


def callback(light_color, state):
    if state:
        print(light_color)
        GPIO.output(PIN_BY_LED_COLOR[light_color], True)


async def main():
    await asyncio.gather(
        watchers.EventWatcher(50, 5, partial(callback, 'red')).run(),
        watchers.EventWatcher(10, 5, partial(callback, 'yellow')).run(),
    )

def run():
    try:
        asyncio.run(main())
    except:
        traceback.print_exc()
    finally:
        GPIO.cleanup()

init()
run()
