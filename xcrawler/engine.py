"""
    engine
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from collections import defaultdict


class CrawlerEngine(object):
    def __init__(self):
        self._extensions = defaultdict(list)
        self._pipelines = defaultdict(list)

    def start(self):
        pass

    def stop(self):
        pass

    def crawl(self, spider_klass, *args, **kwargs):
        pass

    def add_extension(self, ext, priority, bind_spiders):
        pass

    def add_pipeline(self, pipe, priority, bind_spiders):
        pass
