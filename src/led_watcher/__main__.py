import asyncio
import traceback
import logging

from RPi import GPIO

from led_watcher import watchers, callbacks
from led_watcher.constants import BTN, PIN_BY_LED_COLOR, BEEP
from led_watcher.status import status
from led_watcher.controller import main


# Init logger
LOGGER = logging.getLogger('led_watcher')
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)


def patch():
    gpio_output = GPIO.output

    def _output(pin, val):
        status[pin] = val
        gpio_output(pin, val)

    GPIO.output = _output


def init():
    """Init GPIO pins"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BTN, GPIO.IN, GPIO.PUD_DOWN)
    patch()

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


# async def main():
all_watchers = [
    watchers.EventWatcher(
        level_range=(logging.ERROR, logging.ERROR + 50),
        range_state=30,
        interval=5,
    ),
    watchers.EventWatcher(
        level_range=(logging.WARNING, logging.ERROR),
        range_state=20,
        interval=30,
    ),
    watchers.TimeWatcher(
        timetuple=(11, 45),
        interval=5,
    ),
    watchers.TimeWatcher(
        timetuple=(18, 0),
        interval=5,
    ),
    watchers.TimeWatcher(
        timetuple=(23, 48),
        interval=5,
    ),
    watchers.CycleWatcher(
        interval=3,
    ),
]


try:
    LOGGER.info('Start watching..')
    init()
    asyncio.run(main(all_watchers))
except KeyboardInterrupt:
    LOGGER.info('Stop..')
except:
    LOGGER.error(traceback.format_exc())
finally:
    GPIO.cleanup()
    print('Cleaned up.')
