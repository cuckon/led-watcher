import asyncio

from led_watcher import callbacks


class CoroutineFactory:
    """Make fresh coroutine with given coroutine."""
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def make(self):
        async def _call():
            return await self.func(*self.args, **self.kwargs)
        return _call()


callbacks_by_signal = {
    0:  # Heartbeat
    [
        CoroutineFactory(callbacks.blink_if_off, 'blue', 0.001),
    ],

    10: # Info
    [
        CoroutineFactory(callbacks.turn_on, 'blue'),
        CoroutineFactory(callbacks.beep, 1, 0.005, 0),
    ],
    20: # Warning
    [
        CoroutineFactory(callbacks.turn_on, 'yellow'),
        CoroutineFactory(callbacks.beep, 2, 0.05, 0.1),
    ],
    30: # Error
    [
        CoroutineFactory(callbacks.turn_on, 'red'),
        CoroutineFactory(callbacks.beep, 4, 0.03, 0.03),
    ],
    40: # Network Problem
    [
    ],
}


class Caller:
    """Launches the watcher and handles its state with proper callbacks."""
    def __init__(self, watcher):
        self.watcher = watcher

    async def run(self):
        async for state in self.watcher.watch():
            callbacks = callbacks_by_signal[state]
            asyncio.gather(*(c.make() for c in callbacks))


async def main(watchers):
    """Launches all the watchers."""
    await asyncio.gather(*[Caller(w).run() for w in watchers])
