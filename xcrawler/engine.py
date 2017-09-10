"""
    engine
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from collections import defaultdict
from .helpers import run_hook_method


class CrawlerEngine(object):
    def __init__(self):
        self._extensions = defaultdict(list)
        self._pipelines = defaultdict(list)
        self._spiders = []

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def spiders(self):
        pass

    def crawl(self, spider_klass, *args, **kwargs):
        pass

    @property
    def extensions(self):
        pass

    def add_extension(self, ext, priority, bind_spiders):
        pass

    @property
    def pipelines(self):
        pass

    def add_pipeline(self, pipe, priority, bind_spiders):
        pass

    def _on_spider_started(self, spider):
        run_hook_method(self.spiders, 'on_spider_started', spider)
        run_hook_method(self.extensions, 'on_spider_started', spider)
        run_hook_method(self.pipelines, 'on_spider_started', spider)

    def _on_spider_stopped(self, spider):
        run_hook_method(self.spiders, 'on_spider_stopped', spider)
        run_hook_method(self.extensions, 'on_spider_stopped', spider)
        run_hook_method(self.pipelines, 'on_spider_stopped', spider)

    def _on_spider_idle(self, spider):
        run_hook_method(self.spiders, 'on_spider_idle', spider)
        run_hook_method(self.extensions, 'on_spider_idle', spider)
        run_hook_method(self.pipelines, 'on_spider_idle', spider)

