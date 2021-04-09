import enum
import asyncio
import datetime
import logging

import requests


url_events = (
    'http://eventlog.rs.netease.com/api/v1/events?level__gte={}&level__lt={}'
    '&timestamp__gt={}'
    .format
)


class WatcherBase:
    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)

    def state(self):
        return 0

    async def run(self):
        while True:
            self.callback(self.state())
            await asyncio.sleep(self.interval)



# class TimerWatcher(WatcherBase):
#     def __init__(self, check_point):
#         self._state = False


class EventWatcher(WatcherBase):
    def __init__(self, level_range, interval, callback):
        super(EventWatcher, self).__init__(interval, callback)
        self.level_range = level_range
        self._last_check_point = datetime.datetime.now() - \
            datetime.timedelta(seconds=self.interval)

    def state(self):
        url = url_events(
            self.level_range[0], self.level_range[1],
            self._last_check_point.isoformat()
        )
        self._last_check_point = datetime.datetime.now()

        response = requests.get(url)
        if response.status_code != 200:
            self.logger.error(response.text)
            return 1

        data = response.json()
        if data['count']:
            self.logger.debug(data['data'])
            return 1
        return 0
