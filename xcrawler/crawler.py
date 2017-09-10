"""
    crawler
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
from .errors import InvalidExtensionError, InvalidPipelineError

__all__ = ['Crawler']

logger = logging.getLogger(__name__)


class Crawler(object):
    def __init__(self, settings=None, loglevel='DEBUG'):
        self._loglevel = loglevel
        self.settings = settings
        self._engine = None
        self._init_log()

    def start(self):
        self._engine.start()

    def stop(self):
        self._engine.stop()

    def crawl(self, spider_class, *args, **kwargs):
        self._engine.add(spider_class, *args, **kwargs)

    def register_extension(self, extension, priority, bind_spiders=None):
        """An extension with the lowest priority is the closest one
         to the crawler engine."""
        self._validate_extension(extension)
        self._engine.add_extension()

    def _validate_extension(self, extension):
        """An extension must implements :meth:`process_request`.
        Other methods can be implemented:
        - :meth:`spider_started`
        - :meth:`spider_stopped`
        - :meth:`crawler_started`
        - :meth:`crawler_stopped`
        - :meth:`process_response`
        """
        if not extension:
            raise InvalidExtensionError

    @staticmethod
    def _wrap_extension(extension, priority, bind_spiders):
        setattr(extension, 'priority', priority)
        setattr(extension, 'bound_spiders', bind_spiders)
        return extension

    def register_pipeline(self, pipeline, priority, bind_spiders=None):
        """A pipeline with the lowest priority is the closest one
        to the crawler engine"""
        self._engine.add_pipeline(pipeline, priority, bind_spiders)

    def _validate_pipeline(self, pipeline):
        """A pipeline class must implements :meth:`process_item`.
        Other methods can be implemented:
        - :meth:`spider_started`
        - :meth:`spider_stopped`
        - :meth:`crawler_started`
        - :meth:`crawler_stopped`
        """
        if not pipeline:
            raise InvalidPipelineError

    @staticmethod
    def _wrap_pipeline(pipeline, priority, bind_spiders=None):
        setattr(pipeline, 'priority', priority)
        setattr(pipeline, 'bound_spiders', bind_spiders)
        return pipeline

    def _init_log(self):
        logging.basicConfig(format='[%(asctime)s][%(module)s.%(lineno)d][%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=getattr(logging, self._loglevel, logging.DEBUG),
                            handlers=[logging.NullHandler])
