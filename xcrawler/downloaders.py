"""
    downloaders
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import requests
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from .errors import (UnsupportedRequestMethod, HTTPTimeoutError,
                     HTTPStatusError, HTTPConnectionError)
from .http import Request, Response

logger = logging.getLogger(__name__)


class BaseDownloader(object):
    name = 'base_downloader'

    def __init__(self, max_workers=None, download_timeout=None):
        self._max_workers = max_workers
        self._download_timeout = download_timeout if \
            download_timeout is not None else 60

    def download(self, reqs=None):
        for req in reqs:
            yield self.send_request(req)

    def send_request(self, req):
        if req is None:
            return

        assert isinstance(req, Request)

        try:
            logger.debug('[{}]Send request: {}'.format(self.name, req))
            if req.method == 'GET':
                resp = requests.get(req.url, headers=req.headers,
                                    cookies=req.cookies,
                                    timeout=self._download_timeout)
            elif req.method == 'POST':
                resp = requests.post(req.url, headers=req.headers,
                                     cookies=req.cookies,
                                     data=req.data,
                                     timeout=self._download_timeout)
            else:
                raise UnsupportedRequestMethod('method {!s} is not allowed'.format(req.method))

            new_resp = Response(resp.url, resp.status_code, resp.content,
                                resp.apparent_encoding, req,
                                resp.cookies, resp.headers,
                                resp.reason)
            try:
                resp.raise_for_status()
            except requests.HTTPError:
                return new_resp, HTTPStatusError()
            else:
                return new_resp, None
        except requests.Timeout:
            return req, HTTPTimeoutError()
        except requests.ConnectionError:
            return req, HTTPConnectionError()


class ThreadPoolDownloader(BaseDownloader):
    name = 'thread_pool_downloader'

    def download(self, reqs=None):
        if reqs is None:
            return None

        with ThreadPoolExecutor(self._max_workers) as executor:
            futures = []
            for req in reqs:
                futures.append(executor.submit(self.send_request, req))

            for future in as_completed(futures):
                yield future.result()


class ProcessPoolDownloader(BaseDownloader):
    name = 'process_pool_downloader'

    def download(self, reqs=None):
        if reqs is None:
            return None

        with ProcessPoolExecutor(self._max_workers) as executor:
            futures = []
            for req in reqs:
                futures.append(executor.submit(self.send_request, req))

            for future in as_completed(futures):
                yield future.result()


try:
    from gevent.pool import Group
except ImportError:
    class GeventDownloader(BaseDownloader):
        pass
else:
    from gevent import monkey, spawn
    from gevent.pool import Pool
    from gevent.queue import Queue


    class GeventDownloader(BaseDownloader):
        def __init__(self, max_workers=None, download_timeout=None):
            super().__init__(max_workers, download_timeout)

        def download(self, reqs=None):
            pass

__all__ = ['ThreadPoolDownloader', 'ProcessPoolDownloader',
           'GeventDownloader', 'BaseDownloader']
