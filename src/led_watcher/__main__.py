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


async def turn_on(light_color):
    """ Turn on light blinkly.
    """
    for i in range(10):
        await blink(light_color, 0.1)
    GPIO.output(PIN_BY_LED_COLOR[light_color], True)


async def blink(light_color, duration=0.05):
    pin = PIN_BY_LED_COLOR[light_color]
    GPIO.output(pin, True)
    await asyncio.sleep(duration)
    GPIO.output(pin, False)
    await asyncio.sleep(duration)


async def main():
    all_watchers = [
        watchers.EventWatcher(
            level_range=(logging.ERROR, logging.ERROR + 50),
            interval=5,
            callbacks=[
                (turn_on, ['red']),
                (beep_error, []),
            ]
        ),
        watchers.EventWatcher(
            level_range=(logging.WARNING, logging.ERROR),
            interval=5,
            callbacks=[
                (turn_on, ['yellow']),
                (beep_warning, []),
            ]
        ),
        watchers.TimeWatcher(
            timetuple=(11, 45),
            interval=5,
            callbacks=[
                (turn_on, ['blue']),
                (beep_info, []),
            ]
        ),
        watchers.TimeWatcher(
            timetuple=(18, 0),
            interval=5,
            callbacks=[
                (turn_on, ['blue']),
                (beep_info, []),
            ]
        ),
        watchers.CycleWatcher(
            interval=1,
            callbacks=[
                (blink, ['blue']),
            ]
        ),
    ]
    # await all_watchers[0].run()
    await asyncio.gather(*[w.run() for w in all_watchers])


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
