import asyncio
import traceback
import logging

from RPi import GPIO

from led_watcher import watchers, callbacks
from led_watcher.constants import BTN, PIN_BY_LED_COLOR, BEEP
from led_watcher.status import status


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


async def main():
    all_watchers = [
        watchers.EventWatcher(
            level_range=(logging.ERROR, logging.ERROR + 50),
            interval=5,
            callbacks=[
                (callbacks.turn_on, ['red']),
                (callbacks.beep_error, []),
            ]
        ),
        watchers.EventWatcher(
            level_range=(logging.WARNING, logging.ERROR),
            interval=30,
            callbacks=[
                (callbacks.turn_on, ['yellow']),
                (callbacks.beep_warning, []),
            ]
        ),
        watchers.TimeWatcher(
            timetuple=(11, 45),
            interval=5,
            callbacks=[
                (callbacks.turn_on, ['blue']),
                (callbacks.beep_info, []),
            ]
        ),
        watchers.TimeWatcher(
            timetuple=(18, 0),
            interval=5,
            callbacks=[
                (callbacks.turn_on, ['blue']),
                (callbacks.beep_info, []),
            ]
        ),
        watchers.TimeWatcher(
            timetuple=(23, 48),
            interval=5,
            callbacks=[
                (callbacks.turn_on, ['blue']),
                (callbacks.beep_info, []),
            ]
        ),
        watchers.CycleWatcher(
            interval=3,
            callbacks=[
                (callbacks.blink_if_off, ['blue', 0.01]),
            ]
        ),
    ]
    # await all_watchers[0].run()
    await asyncio.gather(*[w.run() for w in all_watchers])


try:
    LOGGER.info('Start watching..')
    init()
    asyncio.run(main())
except KeyboardInterrupt:
    LOGGER.info('Stop..')
except:
    LOGGER.error(traceback.format_exc())
finally:
    GPIO.cleanup()
    print('Cleaned up.')
