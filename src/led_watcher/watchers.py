import os
import asyncio
import datetime
import logging
import traceback

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


url_events = (
    f'{os.environ["EVENTLOG_SERVER"]}/api/v1/events'
    '?level__gte={}&level__lt={}'
    '&timestamp__gt={}'
    .format
)


class WatcherBase:
    def __init__(self, interval):
        self.interval = interval
        self.time_delta = datetime.timedelta(seconds=interval)
        self._last_check_point = datetime.datetime.now() - self.time_delta

        self.logger = logging.getLogger(__name__)

    def state(self):
        self._last_check_point = datetime.datetime.now()
        return 0

    async def watch(self):
        while True:
            await asyncio.sleep(self.interval)
            yield self.state()


# TODO: Can be optimized by sleep (target time - current)
class TimeWatcher(WatcherBase):
    def __init__(self, timetuple, interval):
        super(TimeWatcher, self).__init__(interval)
        self.time = datetime.time(*timetuple)

    def state(self):
        now = datetime.datetime.now()

        # TODO: be cautious of the edge cases?
        hit = self._last_check_point.time() < self.time <= now.time()

        self._last_check_point = now
        return 10 if hit else 0


class CycleWatcher(WatcherBase):
    def state(self):
        return 0


class EventWatcher(WatcherBase):
    def __init__(self, level_range, range_state, interval):
        super(EventWatcher, self).__init__(interval)
        self.level_range = level_range
        self.session = requests.Session()
        self.range_state = range_state
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[502, 503, 504]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def state(self):
        url = url_events(
            self.level_range[0], self.level_range[1],
            self._last_check_point.isoformat()
        )

        # TODO: rename `state()` properly
        super(EventWatcher, self).state()   # update

        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return 40

        if response.status_code != 200:
            self.logger.error(response.text)
            return 40

        data = response.json()
        if data['count']:
            self.logger.debug(data['data'])
            return self.range_state

        return 0
