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
        self.crawler = crawler
        self._scheduler = crawler.scheduler()
        self._downloader = crawler.downloader()
        self._spiders = {}

    def start(self):
        logger.info('Start crawler engine')
        self.crawler.on_crawler_started()
        for s in self.spiders:
            self.crawler.on_spider_started(s)

    def stop(self):
        logger.info('Start crawler engine')
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
