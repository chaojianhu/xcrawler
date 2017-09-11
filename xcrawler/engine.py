"""
    engine
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
import threading
import time

from collections import deque, Mapping
from queue import Queue, Full, Empty
from .http import Request, Response

logger = logging.getLogger(__name__)


class CrawlerEngine(object):
    _scheduler_lock = threading.Lock()

    def __init__(self, crawler):
        self._is_running = False
        self.crawler = crawler

        self._concurrent_requests = crawler.settings.get('CONCURRENT_REQUESTS', 8)
        self._scheduler = crawler.scheduler(2 * self._concurrent_requests)
        self._results_queue = Queue(self._scheduler.maxsize)
        self._download_delay = crawler.settings.get('CONCURRENT_REQUESTS', 0)
        self._downloader = crawler.downloader(
            self._concurrent_requests,
            crawler.settings.get('DOWNLOAD_TIMEOUT'))

        self._spiders = {}

    def start(self):
        if self._is_running:
            raise RuntimeError('Crawler engine is running now')

        logger.info('Start crawler engine')
        self._is_running = True
        self._scheduler.clear()
        self.crawler.on_crawler_started()
        for s in self.spiders:
            self.crawler.on_spider_started(s)

        self._init_scheduler_with_seed_requests()

        # start downloader thread
        down_thread = threading.Thread(target=self._run_downloader,
                                       daemon=True)
        down_thread.start()
        self._run_until_complete()

    def _init_scheduler_with_seed_requests(self):
        spiders = deque(self.spiders)

        while len(spiders) > 0 and \
                not self._scheduler.is_full():
            spider = spiders.pop()
            try:
                req = self._process_request(next(spider.start_requests()))
                if req is None:
                    continue

                self._scheduler.add(req)
            except StopIteration:
                continue
            else:
                # push back to the deque for the next loop
                spiders.appendleft(spider)

    def _run_downloader(self):
        def download():
            reqs = []
            for _ in range(self._concurrent_requests):
                if self._scheduler.is_empty():
                    break
                reqs.append(self._scheduler.pop())

            for result in self._downloader.download(reqs):
                self._results_queue.put(result)

        tick = 0
        download_delay = self._download_delay * 1000

        while self._is_running:
            if download_delay > 0 and tick < download_delay:
                tick += 1
                continue
            else:
                tick = 0

                if self._results_queue.qsize() < self._results_queue.maxsize:
                    threading.Thread(target=download, daemon=True)

            # sleep 1 ms
            time.sleep(.001)

    def _run_until_complete(self):
        while self._is_running:
            pass

            # self.stop()

    def _process_request(self, request):
        """Invoke all the extensions to process the input request.
        Possible results are:
        - :class:`Request`
        - None
        """
        for ext in self.crawler.global_extensions \
                + self.crawler.spider_extensions:
            request = ext.process_request(request, request.spider)
            if request is None:
                return None

        return request

    def _process_response(self, response):
        """Invoke all the extensions to process the input response.
        Possible results are:
        - :class:`Response`
        - :class:`Request`
        - None
        """
        for ext in self.crawler.global_extensions \
                + self.crawler.spider_extensions:
            if isinstance(response, Response):
                response = ext.process_response(response,
                                                response.request,
                                                response.request.spider)
            elif isinstance(response, Request):
                return response
            else:
                return None

        return response

    def _process_http_error(self, req_or_resp, error):
        """Invoke all the extensions to process the error result.
        Possible results are:
        - :class:`Request`
        - None
        """
        if error is None:
            return None

        for ext in self.crawler.global_extensions \
                + self.crawler.spider_extensions:
            if isinstance(req_or_resp, Request):
                req_or_resp = ext.process_http_error(error, None,
                                                     req_or_resp,
                                                     req_or_resp.spider)
            elif isinstance(req_or_resp, Response):
                req_or_resp = ext.process_http_error(error,
                                                     req_or_resp,
                                                     req_or_resp.request,
                                                     req_or_resp.request.spider)
            else:
                return None

        return req_or_resp if \
            isinstance(req_or_resp, Request) else None

    def _process_item(self, item, request):
        """Invoke all the extensions to process the error result.
        Possible results are:
        - :class:`Item`
        - None
        """
        for pipe in self.crawler.global_pipelines + \
                self.crawler.spider_pipelines:
            if isinstance(item, Mapping):
                item = pipe.process_item(item, request, request.spider)
            else:
                return None

        return item

    def stop(self):
        if not self._is_running:
            raise RuntimeError('Crawler engine has already stopped')

        logger.info('Start crawler engine')
        self._is_running = False
        self._scheduler.clear()
        self.crawler.on_crawler_stopped()
        for s in self.spiders:
            self.crawler.on_spider_stopped(s)

    def spider_idle(self, spider):
        logger.debug('Spider {} is idle'.format(spider))
        self.crawler.on_spider_idle(spider)

    @property
    def spiders(self):
        return self._spiders.values()

    def crawl(self, spider_klass, *args, **kwargs):
        spider = spider_klass(*args, **kwargs)
        setattr(spider, 'crawler', self.crawler)
        self._spiders[spider.name] = spider
