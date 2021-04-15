import asyncio

from RPi import GPIO
from led_watcher.constants import PIN_BY_LED_COLOR, BEEP
from led_watcher.status import status


async def beep_info():
    GPIO.output(BEEP, True)
    await asyncio.sleep(0.005)
    GPIO.output(BEEP, False)


async def beep_warning():
    for _ in range(2):
        GPIO.output(BEEP, True)
        await asyncio.sleep(0.05)
        GPIO.output(BEEP, False)
        await asyncio.sleep(0.1)


async def beep_error():
    for _ in range(4):
        GPIO.output(BEEP, True)
        await asyncio.sleep(0.03)
        GPIO.output(BEEP, False)
        await asyncio.sleep(0.03)


async def turn_on(light_color):
    """ Turn on light blinkly.
    """
    for _ in range(10):
        await blink(light_color, 0.1)
    GPIO.output(PIN_BY_LED_COLOR[light_color], True)


async def blink(light_color, duration=0.05):
    pin = PIN_BY_LED_COLOR[light_color]
    GPIO.output(pin, True)
    await asyncio.sleep(duration)
    GPIO.output(pin, False)
    await asyncio.sleep(duration)


async def blink_if_off(light_color, duration):
    if status.get(PIN_BY_LED_COLOR[light_color]):
        return
    await blink(light_color, duration)
