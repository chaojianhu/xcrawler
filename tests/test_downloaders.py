"""
    test_downloaders
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import pytest
from xcrawler.http import Request, Response
from xcrawler.downloaders import (BaseDownloader, ProcessPoolDownloader,
                                  ThreadPoolDownloader, GeventDownloader)
from xcrawler.errors import HTTPStatusError, HTTPTimeoutError, HTTPConnectionError

import logging

logging.basicConfig()
logging.getLogger('xcrawler').setLevel(level=logging.DEBUG)


class FooSpider:
    name = 'foo'


spider = FooSpider()


def test_base_downloader(monkeypatch):
    def download(self, reqs):
        for req in reqs:
            yield self.send_request(req)

    monkeypatch.setattr(BaseDownloader, 'download', download)

    req = Request('https://httpbin.org', spider)
    result = BaseDownloader().send_request(req)
    assert result[0].status == 200
    assert result[-1] is None

    req = Request('http://example.httpbin.com', spider)
    result = BaseDownloader().send_request(req)
    assert result[0] == req
    assert isinstance(result[-1], HTTPConnectionError)

    req = Request('http://httpbin.com', spider)
    result = BaseDownloader(download_timeout=0.001).send_request(req)
    assert result[0] == req
    assert isinstance(result[-1], HTTPTimeoutError)

    req = Request('http://www.chriscabin.com/not/found/error', spider)
    result = BaseDownloader().send_request(req)
    assert result[0].status == 404
    assert isinstance(result[-1], HTTPStatusError)


def test_thread_pool_downloader():
    d = ThreadPoolDownloader(max_workers=20)
    reqs = [Request('https://now.httpbin.org/', spider) for _ in range(1, 20)]

    for result in d.download(reqs):
        assert result[0].status == 200
        assert result[-1] is None
        assert 'now' in result[0].text


def test_process_pool_downloader():
    d = ProcessPoolDownloader(max_workers=5)
    reqs = [Request('https://now.httpbin.org/', spider) for _ in range(1, 5)]

    for result in d.download(reqs):
        assert result[0].status == 200
        assert result[-1] is None
        assert 'now' in result[0].text


def test_gevent_pool_downloader():
    # from gevent import monkey
    # monkey.patch_socket()

    d = GeventDownloader(max_workers=5)
    reqs = [Request('https://now.httpbin.org/', spider) for _ in range(5)]

    for result in d.download(reqs):
        assert result[0].status == 200
        assert result[-1] is None
        assert 'now' in result[0].text
