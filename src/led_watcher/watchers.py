import enum
import asyncio
import datetime

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
    def __init__(self, level, interval, callback):
        super(EventWatcher, self).__init__(interval, callback)
        self.level = level
        self._last_check_point = datetime.datetime.now() - \
            datetime.timedelta(seconds=self.interval)

    def state(self):
        url = url_events(
            self.level, self.level + 10, self._last_check_point.isoformat()
        )
        self._last_check_point = datetime.datetime.now()

        response = requests.get(url)
        if response.status_code != 200:
            print(response.text)
            return 1

        if response.json()['count']:
            return 1
        return 0
