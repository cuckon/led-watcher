import os
import asyncio
import datetime
import logging

import requests


url_events = (
    f'{os.environ["EVENTLOG_SERVER"]}/api/v1/events'
    '?level__gte={}&level__lt={}'
    '&timestamp__gt={}'
    .format
)


class WatcherBase:
    def __init__(self, interval, callbacks):
        self.interval = interval
        self.time_delta = datetime.timedelta(seconds=interval)
        self.callbacks = callbacks
        self._last_check_point = datetime.datetime.now() - self.time_delta

        self.logger = logging.getLogger(__name__)

    def state(self):
        self._last_check_point = datetime.datetime.now()
        return 0

    async def run(self):
        while True:
            if self.state():
                await asyncio.gather(
                    *[coro(*args) for coro, args in self.callbacks]
                )
            await asyncio.sleep(self.interval)


class TimeWatcher(WatcherBase):
    def __init__(self, timetuple, interval, callbacks):
        super(TimeWatcher, self).__init__(interval, callbacks)
        self.time = datetime.time(*timetuple)

    def state(self):
        now = datetime.datetime.now()

        # TODO: be cautious of the edge cases?
        hit = self._last_check_point.time() < self.time <= now.time()

        self._last_check_point = now
        return hit


class CycleWatcher(WatcherBase):
    def state(self):
        return 1


class EventWatcher(WatcherBase):
    def __init__(self, level_range, interval, callbacks):
        super(EventWatcher, self).__init__(interval, callbacks)
        self.level_range = level_range

    def state(self):
        url = url_events(
            self.level_range[0], self.level_range[1],
            self._last_check_point.isoformat()
        )

        # TODO: rename `state()` properly
        super(EventWatcher, self).state()   # update

        response = requests.get(url)
        if response.status_code != 200:
            self.logger.error(response.text)
            return 1

        data = response.json()
        if data['count']:
            self.logger.debug(data['data'])
            return 1
        return 0
