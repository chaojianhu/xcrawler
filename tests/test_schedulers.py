"""
    test_schedulers
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler.schedulers.fifo import FIFOScheduler
from xcrawler.schedulers.filo import FILOScheduler
from xcrawler.schedulers.priority import PriorityBasedScheduler


def test_fifo_scheduler():
    sch = FIFOScheduler()
    assert len(sch) == 0
    sch.add(0)
    sch.add(1)
    assert len(sch) == 2
    assert 0 == sch.pop()
    assert 1 == sch.pop()
    assert sch.pop() is None

    sch.add(1)
    sch.add(2)
    assert 1 == sch.pop()
    sch.add(3)
    assert 2 == sch.pop()

    sch.clear()
    assert len(sch) == 0


def test_filo_scheduler():
    sch = FILOScheduler()
    assert len(sch) == 0
    sch.add(0)
    sch.add(1)
    assert len(sch) == 2
    assert 1 == sch.pop()
    assert 0 == sch.pop()
    assert sch.pop() is None

    sch.add(1)
    sch.add(2)
    assert 2 == sch.pop()
    sch.add(3)
    assert 3 == sch.pop()

    sch.clear()
    assert len(sch) == 0


def test_priority_based_scheduler():
    from collections import namedtuple

    Req = namedtuple('Req', 'val, priority')

    sch = PriorityBasedScheduler()
    assert len(sch) == 0
    sch.add(Req(1, 1))
    sch.add(Req(2, 0))
    assert len(sch) == 2
    assert Req(2, 0) == sch.pop()
    assert Req(1, 1) == sch.pop()
    assert sch.pop() is None

    sch.add(Req(1, 0))
    sch.add(Req(2, 0))
    assert Req(1, 0) == sch.pop()
    assert Req(2, 0) == sch.pop()

    sch.add(Req(3, 1))
    sch.add(Req(4, 2))
    sch.add(Req(5, 0))
    assert Req(5, 0) == sch.pop()
    assert Req(3, 1) == sch.pop()
    assert Req(4, 2) == sch.pop()

    sch.add(Req(3, 10))
    sch.clear()
    assert len(sch) == 0
