"""
    crawler
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
from .engine import CrawlerEngine
from .downloaders import ThreadingDownloader as Downloader
from .schedulers.fifo import FIFOScheduler as Scheduler
from .errors import InvalidExtensionError, InvalidPipelineError
from .helpers import run_hook_method

__all__ = ['Crawler']

logger = logging.getLogger(__name__)


class Crawler(object):
    def __init__(self, loglevel='DEBUG', **kwargs):
        self._loglevel = loglevel
        self.settings = kwargs
        self._scheduler_klass = Scheduler
        self._downloader_klass = Downloader
        self._engine = CrawlerEngine()
        self._init_log()

    def __repr__(self):
        return 'Crawler({!r}, {!r})'.format(self._loglevel, self.settings)

    def start(self):
        self._engine.start()

    def _on_crawler_started(self):
        run_hook_method(self._engine.spiders, 'on_crawler_started', self)
        run_hook_method(self._engine.extensions, 'on_crawler_started', self)
        run_hook_method(self._engine.pipelines, 'on_crawler_started', self)

    def stop(self):
        self._engine.stop()

    def _on_crawler_stopped(self):
        run_hook_method(self._engine.spiders, 'on_crawler_stopped')
        run_hook_method(self._engine.extensions, 'on_crawler_stopped', self)
        run_hook_method(self._engine.pipelines, 'on_crawler_stopped', self)

    def crawl(self, spider_klass, *args, **kwargs):
        self._engine.crawl(spider_klass, *args, **kwargs)

    def add_extension(self, extension, priority=0, bind_spiders=None):
        """An extension with the lowest priority is the closest one
         to the crawler engine."""
        self._validate_extension(extension)
        self._engine.add_extension(extension, priority, bind_spiders)

    @staticmethod
    def _validate_extension(extension):
        """An extension must implements :meth:`process_request`.
        Other methods can be implemented:
        - :meth:`on_spider_started`
        - :meth:`on_spider_stopped`
        - :meth:`on_crawler_started`
        - :meth:`on_crawler_stopped`
        - :meth:`process_response`
        """
        if not extension:
            raise InvalidExtensionError

        if not hasattr(extension, 'process_request'):
            raise InvalidExtensionError('missing method `{}`'.format('process_request'))

    def add_pipeline(self, pipeline, priority=0, bind_spiders=None):
        """A pipeline with the lowest priority is the closest one
        to the crawler engine"""
        self._validate_pipeline(pipeline)
        self._engine.add_pipeline(pipeline, priority, bind_spiders)

    @staticmethod
    def _validate_pipeline(pipeline):
        """A pipeline class must implements :meth:`process_item`.
        Other methods can be implemented:
        - :meth:`on_spider_started`
        - :meth:`on_spider_stopped`
        - :meth:`on_on_crawler_started`
        - :meth:`crawler_stopped`
        """
        if not pipeline:
            raise InvalidPipelineError

        if not hasattr(pipeline, 'process_item'):
            raise InvalidExtensionError('missing method `{}`'.format('process_item'))

    def _init_log(self):
        logging.basicConfig(format='[%(asctime)s][%(module)s.%(lineno)d][%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=getattr(logging, self._loglevel, logging.DEBUG),
                            handlers=[logging.NullHandler])
