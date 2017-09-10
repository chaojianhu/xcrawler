"""
    priority based scheduler
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from heapq import heappop, heappush


class PriorityBasedScheduler(object):
    def __init__(self):
        self._requests = []

    def __repr__(self):
        return 'FIFOScheduler()'

    def add(self, req):
        heappush(self._requests, (req.priority, 0, req))

    def pop(self):
        try:
            _, _, req = heappop(self._requests)
            return req
        except IndexError:
            return None

    def clear(self):
        self._requests.clear()

    def __len__(self):
        return len(self._requests)
