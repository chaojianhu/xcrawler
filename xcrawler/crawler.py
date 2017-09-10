"""
    crawler
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
from operator import itemgetter
from collections import defaultdict

from .engine import CrawlerEngine
from .downloaders import ThreadingDownloader as DefaultDownloader
from .schedulers.fifo import FIFOScheduler as DefaultScheduler
from .errors import InvalidExtensionError, InvalidPipelineError
from .helpers import run_hook_method, dict_keys_to_upper

__all__ = ['Crawler']

logger = logging.getLogger(__name__)


class Crawler(object):
    def __init__(self, loglevel='DEBUG', global_extensions=None,
                 global_pipelines=None, scheduler=None, downloader=None,
                 **kwargs):
        self._loglevel = loglevel
        self.settings = dict_keys_to_upper(kwargs)
        self._global_extensions = []
        self._global_pipelines = []
        self._spider_extensions = defaultdict(list)
        self._spider_pipelines = defaultdict(list)

        self.scheduler = scheduler or DefaultScheduler
        self.downloader = downloader or DefaultDownloader
        self._engine = CrawlerEngine(self)

        self._init_log()
        self._install_global_extensions(global_extensions)
        self._install_global_pipelines(global_pipelines)

    def _init_log(self):
        logging.basicConfig(format='[%(asctime)s][%(module)s.%(lineno)d][%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=getattr(logging, self._loglevel, logging.DEBUG))

    def _install_global_extensions(self, extensions):
        """Global extensions, enabled for all the spiders"""
        if extensions is None:
            return None

        for priority, ext in extensions.items():
            self.add_global_extension(ext, priority)

    def _install_global_pipelines(self, pipelines):
        """Global pipelines, enabled for all the pipelines"""
        if pipelines is None:
            return None

        for priority, pipe in pipelines.items():
            self.add_global_pipeline(pipe, priority)

    def __repr__(self):
        return 'Crawler({!r}, **{!r})'.format(self._loglevel, self.settings)

    def start(self):
        logger.info('Start crawler process')

        # sort extensions and pipelines by priority
        self._global_extensions.sort(key=itemgetter(-1))
        self._global_pipelines.sort(key=itemgetter(-1))

        for s in self._spider_extensions:
            self._spider_extensions[s].sort(key=itemgetter(-1))

        for s in self._spider_pipelines:
            self._spider_pipelines[s].sort(key=itemgetter(-1))

        # start the engine now
        self._engine.start()

    @property
    def spiders(self):
        return self._engine.spiders

    def crawl(self, spider_klass, *args, **kwargs):
        if spider_klass is None:
            return

        spider_klass.custom_settings = dict_keys_to_upper(spider_klass.custom_settings)
        self._install_spider_extensions(spider_klass)
        self._install_spider_pipelines(spider_klass)

        logger.info('Prepare to crawl {!r}'.format(spider_klass.name))
        self._engine.crawl(spider_klass, *args, **kwargs)

    def _install_spider_extensions(self, spider_klass):
        extensions = spider_klass.custom_settings.get('SPIDER_EXTENSIONS', {})
        for priority, ext in extensions.items():
            self.add_spider_extension(ext, priority, spider_klass.name)

    def _install_spider_pipelines(self, spider_klass):
        pipelines = spider_klass.custom_settings.get('SPIDER_PIPELINES', {})
        for priority, pipe in pipelines.items():
            self.add_spider_pipeline(pipe, priority, spider_klass.name)

    @property
    def global_extensions(self):
        return [ext for ext, _ in self._global_extensions]

    def add_global_extension(self, ext, priority):
        self._validate_extension(ext)
        logger.debug('[{}] Add extension {!r} with priority {}'.
                     format('GLOBAL',
                            ext.__name__,
                            priority))
        self._global_extensions.append((ext(), priority))

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

    @property
    def global_pipelines(self):
        return [p for p, _ in self._global_pipelines]

    def add_global_pipeline(self, pipe, priority):
        self._validate_pipeline(pipe)
        logger.debug('[{}] Add pipeline {!r} with priority {}'.
                     format('GLOBAL',
                            pipe.__name__,
                            priority))
        self._global_pipelines.append((pipe(), priority))

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

    @property
    def spider_extensions(self):
        return [ext for ext, _ in self._spider_extensions.values()]

    def spider_extensions_by_name(self, spider_name):
        return [ext for ext, _ in self._spider_pipelines.get(spider_name, [])]

    def add_spider_extension(self, ext, priority, spider_name):
        self._validate_extension(ext)
        logger.debug('[{}] Add extension {!r} with priority {}'.
                     format(spider_name.upper(),
                            ext.__name__,
                            priority))
        self._spider_extensions[spider_name].append((ext(), priority))

    @property
    def spider_pipelines(self):
        return [p for p, _ in self._spider_pipelines.values()]

    def spider_pipelines_by_name(self, spider_name):
        return [pipe for pipe, _ in self._spider_pipelines.get(spider_name, [])]

    def add_spider_pipeline(self, pipe, priority, spider_name):
        self._validate_pipeline(pipe)
        logger.debug('[{}] Add pipeline {!r} with priority {}'.
                     format(spider_name.upper(),
                            pipe.__name__,
                            priority))
        self._spider_pipelines[spider_name].append((pipe(), priority))

    # hook signals
    def on_crawler_started(self):
        run_hook_method(self.spiders, 'on_crawler_started', self)
        run_hook_method(self.global_extensions + self.spider_extensions,
                        'on_crawler_started', self)
        run_hook_method(self.global_pipelines + self.spider_pipelines,
                        'on_crawler_started', self)

    def on_crawler_stopped(self):
        run_hook_method(self.spiders, 'on_crawler_stopped', self)
        run_hook_method(self.global_extensions + self.spider_extensions,
                        'on_crawler_stopped', self)
        run_hook_method(self.global_pipelines + self.spider_pipelines,
                        'on_crawler_stopped', self)

    def on_spider_started(self, spider):
        run_hook_method([spider], 'on_spider_started', spider)
        run_hook_method(self.global_extensions + self.spider_extensions,
                        'on_spider_started', spider)
        run_hook_method(self.global_pipelines + self.spider_pipelines,
                        'on_spider_started', spider)

    def on_spider_stopped(self, spider):
        run_hook_method([spider], 'on_spider_stopped', spider)
        run_hook_method(self.global_extensions + self.spider_extensions,
                        'on_spider_stopped', spider)
        run_hook_method(self.global_pipelines + self.spider_pipelines,
                        'on_spider_stopped', spider)

    def on_spider_idle(self, spider):
        run_hook_method([spider], 'on_spider_idle', spider)
        run_hook_method(self.global_extensions + self.spider_extensions,
                        'on_spider_idle', spider)
        run_hook_method(self.global_pipelines + self.spider_pipelines,
                        'on_spider_idle', spider)
