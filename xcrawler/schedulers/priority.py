"""
    priority based scheduler
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import time
from queue import PriorityQueue, Empty


class PriorityBasedScheduler(object):
    def __init__(self, maxsize=None):
        self._requests = PriorityQueue(maxsize or 0)
        self.maxsize = maxsize

    def __repr__(self):
        return 'FIFOScheduler()'

    def add(self, req):
        self._requests.put((req.priority, time.time(), req))

    def pop(self):
        try:
            _, _, req = self._requests.get_nowait()
        except Empty:
            return None
        else:
            return req

    def clear(self):
        while self.pop():
            pass

    def is_full(self):
        return self._requests.full()

    def is_empty(self):
        return self._requests.empty()

    def __len__(self):
        return self._requests.qsize()
