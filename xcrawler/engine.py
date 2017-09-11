"""
    engine
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
import threading
import time
from pprint import pformat
from collections import deque, Mapping
from queue import Queue, Empty

from .http import Request, Response

logger = logging.getLogger(__name__)


class CrawlerEngine(object):
    _engine_lock = threading.Lock()

    def __init__(self, crawler):
        self._is_running = False
        self._idle_timeout = crawler.settings.get('ENGINE_IDLE_TIMEOUT', 5)
        self.crawler = crawler

        self._concurrent_requests = crawler.settings.get('CONCURRENT_REQUESTS', 8)
        self._scheduler = crawler.scheduler(2 * self._concurrent_requests)
        self._results_queue = Queue(self._scheduler.maxsize)
        self._download_delay = crawler.settings.get('CONCURRENT_REQUESTS', 0)
        self._active_downloaders = 0
        self._buffered_requests = deque()

        self._downloader = crawler.downloader(
            self._concurrent_requests,
            crawler.settings.get('DOWNLOAD_TIMEOUT'))

        self._spiders = {}
        self._initial_requests_iters = None

    def start(self):
        if self._is_running:
            raise RuntimeError('Crawler engine is running now')

        logger.info('Start crawler engine')
        self._is_running = True
        self._scheduler.clear()
        self.crawler.on_crawler_started()
        for s in self.spiders:
            self.crawler.on_spider_started(s)

        self._initial_requests_iters = deque([x.start_requests() for x
                                              in self.spiders])
        self._init_scheduler_with_seed_requests()

        # start downloader thread
        down_thread = threading.Thread(target=self._run_downloaders,
                                       daemon=True)
        down_thread.start()
        self._run_until_complete()

    def _init_scheduler_with_seed_requests(self):
        while len(self._initial_requests_iters) > 0 and \
                not self._scheduler.is_full():
            it = self._initial_requests_iters.pop()
            try:
                self.schedule_request(next(it))
            except StopIteration:
                continue
            else:
                # push back to the deque for the next loop
                self._initial_requests_iters.appendleft(it)

    def schedule_request(self, req):
        req = self._process_request(req)
        if isinstance(req, Request):
            self._scheduler.add(req)

    def append_request(self, req):
        self._buffered_requests.append(req)

    def _run_downloaders(self):
        def download():
            with self._engine_lock:
                self._active_downloaders += 1

            reqs = []
            for _ in range(self._concurrent_requests):
                if self._scheduler.is_empty():
                    break
                reqs.append(self._scheduler.pop())

            for result in self._downloader.download(reqs):
                self._results_queue.put(result)

            with self._engine_lock:
                self._active_downloaders -= 1

        tick = 0
        download_delay = self._download_delay * 1000

        while self._is_running:
            if download_delay > 0 and tick < download_delay:
                tick += 1
                continue
            else:
                tick = 0

                if self._results_queue.qsize() < self._results_queue.maxsize:
                    threading.Thread(target=download, daemon=True).start()

            # sleep 1 ms
            time.sleep(.001)

    def _run_until_complete(self):
        idle_count = 0

        while self._is_running:
            try:
                reqresp, err = self._results_queue.get(timeout=.1)
            except Empty:
                if self._active_downloaders <= 0 and \
                        self._scheduler.is_empty() \
                        and len(self._buffered_requests) == 0:
                    idle_count += 1
                    if idle_count * 100 > self._idle_timeout * 1000:
                        break

                    self.engine_idle()
            else:
                idle_count = 0
                if err is None:
                    result = self._process_response(reqresp)
                else:
                    result = self._process_http_error(reqresp, err)

                if isinstance(result, Request):
                    self.append_request(result)

                if isinstance(result, Response):
                    parsed_results = result.callback(result)
                    try:
                        iter(parsed_results)
                    except TypeError:
                        continue

                    for item in parsed_results:
                        if isinstance(item, Request):
                            self.append_request(item)
                        if isinstance(item, Mapping):
                            self._process_item(item, result.request)

            self._init_scheduler_with_seed_requests()
            self._next_batch_requests()

        self._stop()

    def _next_batch_requests(self):
        while not self._scheduler.is_full():
            try:
                self.schedule_request(self._buffered_requests.popleft())
            except IndexError:
                break

    def _process_request(self, request):
        """Invoke all the extensions to process the input request.
        Possible results are:
        - :class:`Request`
        - None
        """
        logger.debug('Processing request: {}'.format(request))
        for ext in self.crawler.global_extensions \
                + self.crawler.spider_extensions:
            if not hasattr(ext, 'process_request'):
                continue

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
        logger.debug('Processing response: {}'.format(response))
        for ext in self.crawler.global_extensions \
                + self.crawler.spider_extensions:
            if not hasattr(ext, 'process_response'):
                continue

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

        logger.debug('Processing error request or '
                     'response: {}'.format(req_or_resp))
        for ext in self.crawler.global_extensions \
                + self.crawler.spider_extensions:
            if not hasattr(ext, 'process_http_error'):
                continue

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
        """Invoke all the extensions to process the parsed items.
        """
        logger.debug('Parsed item for spider {}: {}'.format(request.spider,
                                                            pformat(item)))
        for pipe in self.crawler.global_pipelines + \
                self.crawler.spider_pipelines:
            if not hasattr(pipe, 'process_item'):
                continue

            if isinstance(item, Mapping):
                item = pipe.process_item(item, request, request.spider)
            else:
                return None

    def _stop(self):
        if not self._is_running:
            raise RuntimeError('Crawler engine has already stopped')

        logger.info('Stop crawler engine')
        self._is_running = False
        self._scheduler.clear()
        self.crawler.on_crawler_stopped()
        for s in self.spiders:
            self.crawler.on_spider_stopped(s)

    def engine_idle(self):
        logger.debug('Engine is idle now'.format())
        self.crawler.on_engine_idle()

    @property
    def spiders(self):
        return self._spiders.values()

    def crawl(self, spider_klass, *args, **kwargs):
        spider = spider_klass(*args, **kwargs)
        setattr(spider, 'crawler', self.crawler)
        self._spiders[spider.name] = spider
