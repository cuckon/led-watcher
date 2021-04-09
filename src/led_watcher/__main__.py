import random
import asyncio
import time
import traceback
import sys
import logging
from functools import partial

from RPi import GPIO

from led_watcher import watchers

BTN = 12
PIN_BY_LED_COLOR = dict(
    red = 11,
    yellow = 13,
    blue = 15,
)
BEEP = 16
POLLING_INTERVAL = 0.5
logger = logging.getLogger('led_watcher')


def init():
    # Init GPIO pins
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BTN, GPIO.IN, GPIO.PUD_DOWN)
    for pin in PIN_BY_LED_COLOR.values():
        GPIO.setup(pin, GPIO.OUT)
    GPIO.setup(BEEP, GPIO.OUT)

    GPIO.add_event_detect(
        BTN, GPIO.RISING, callback=on_button_pressed, bouncetime=200
    )

    # Init logger
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)


def on_button_pressed(_):
    for pin in PIN_BY_LED_COLOR.values():
        GPIO.output(pin, False)


def beep_info():
    GPIO.output(BEEP, True)
    time.sleep(0.005)


def beep_warning():
    for i in range(2):
        GPIO.output(BEEP, True)
        time.sleep(0.05)
        GPIO.output(BEEP, False)
        time.sleep(0.05)


def beep_error():
    for i in range(4):
        GPIO.output(BEEP, True)
        time.sleep(0.03)
        GPIO.output(BEEP, False)
        time.sleep(0.03)


# def beep(level):
#     if level < logging.INFO:
#         return
#     if level < logging.WARNING:
#         _beep_info()
#     elif level < logging.ERROR:
#         _beep_warning()
#     else:
#         _beep_error()


def callback(light_color, beep, state):
    if state:
        GPIO.output(PIN_BY_LED_COLOR[light_color], True)
        beep()


async def main():
    error_watcher = watchers.EventWatcher(
        level_range=(40, 60),
        interval=5,
        callback=partial(callback, 'red', beep_error)
    )
    warning_watcher = watchers.EventWatcher(
        level_range=(30, 40),
        interval=5,
        callback=partial(callback, 'yellow', beep_warning)
    )
    await asyncio.gather(
        error_watcher.run(),
        warning_watcher.run(),
    )


def run():
    logger.info('Start watching..')
    try:
        asyncio.run(main())
    except:
        traceback.print_exc()
    finally:
        GPIO.cleanup()

init()
run()
