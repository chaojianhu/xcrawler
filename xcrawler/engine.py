"""
    engine
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging

logger = logging.getLogger(__name__)


class CrawlerEngine(object):
    def __init__(self, crawler):
        self._is_running = False
        self.crawler = crawler
        self._scheduler = crawler.scheduler()
        self._downloader = crawler.downloader(
            crawler.settings.get('CONCURRENT_REQUESTS'),
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

        self._init_seed_requests()
        self._run_until_complete()

    def stop(self):
        if not self._is_running:
            raise RuntimeError('Crawler engine has stopped already')

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

    def _init_seed_requests(self):
        pass

    def _run_until_complete(self):
        self.stop()

    def _process_request(self, request, spider):
        pass

    def _process_response(self, response, request, spider):
        pass

    def _process_item(self, item, request, spider):
        pass
