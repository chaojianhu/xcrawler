"""
    priority based scheduler
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from heapq import heappop, heappush


class PriorityBasedScheduler(object):
    def __init__(self, maxsize=None):
        self._requests = []
        self.maxsize = maxsize or float('inf')
        self._count = 0

    def __repr__(self):
        return 'FIFOScheduler()'

    def add(self, req):
        heappush(self._requests, (req.priority, self._count, req))
        self._count += 1

    def pop(self):
        try:
            _, _, req = heappop(self._requests)
            self._count -= 1
            return req
        except IndexError:
            return None

    def clear(self):
        self._requests.clear()

    def is_full(self):
        return len(self) == self.maxsize

    def is_empty(self):
        return len(self) == 0

    def __len__(self):
        return len(self._requests)
