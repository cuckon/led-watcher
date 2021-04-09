import random
import asyncio
import time
import traceback
import sys
import logging
from functools import partial

from RPi import GPIO

from led_watcher import watchers
from led_watcher.constants import BTN, PIN_BY_LED_COLOR, BEEP


# Init logger
logger = logging.getLogger('led_watcher')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def init():
    """Init GPIO pins"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BTN, GPIO.IN, GPIO.PUD_DOWN)
    for pin in list(PIN_BY_LED_COLOR.values()) + [BEEP]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)

    GPIO.add_event_detect(
        BTN,
        GPIO.RISING,
        callback=on_button_pressed,
        bouncetime=200
    )


def on_button_pressed(_):
    for pin in PIN_BY_LED_COLOR.values():
        GPIO.output(pin, False)


async def beep_info():
    GPIO.output(BEEP, True)
    await asyncio.sleep(0.005)
    GPIO.output(BEEP, False)


async def beep_warning():
    for i in range(2):
        GPIO.output(BEEP, True)
        await asyncio.sleep(0.05)
        GPIO.output(BEEP, False)
        await asyncio.sleep(0.1)


async def beep_error():
    for i in range(4):
        GPIO.output(BEEP, True)
        await asyncio.sleep(0.03)
        GPIO.output(BEEP, False)
        await asyncio.sleep(0.03)


async def turn_on(light_color, blink=False):
    pin = PIN_BY_LED_COLOR[light_color]
    if blink:
        for i in range(10):
            GPIO.output(pin, True)
            await asyncio.sleep(0.1)
            GPIO.output(pin, False)
            await asyncio.sleep(0.1)
    GPIO.output(pin, True)


async def callback(light_color, beep, state):
    if state:
        await asyncio.gather(
            turn_on(light_color, True),
            beep(),
        )


async def main():
    error_watcher = watchers.EventWatcher(
        level_range=(logging.ERROR, logging.ERROR + 50),
        interval=5,
        callback=partial(callback, 'red', beep_error)
    )
    warning_watcher = watchers.EventWatcher(
        level_range=(logging.WARNING, logging.ERROR),
        interval=5,
        callback=partial(callback, 'yellow', beep_warning)
    )
    launch_watcher = watchers.TimeWatcher(
        timetuple=(22, 7),
        interval=5,
        callback=partial(callback, 'blue', beep_info)
    )
    dinner_watcher = watchers.TimeWatcher(
        timetuple=(22, 8),
        interval=5,
        callback=partial(callback, 'blue', beep_info)
    )
    await asyncio.gather(
        error_watcher.run(),
        warning_watcher.run(),
        launch_watcher.run(),
        dinner_watcher.run(),
    )


try:
    logger.info('Start watching..')
    init()
    asyncio.run(main())
except KeyboardInterrupt:
    logger.info('Stop..')
except:
    logger.error(traceback.format_exc())
finally:
    GPIO.cleanup()
    print('Cleaned up.')
