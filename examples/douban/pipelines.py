"""
    pipelines
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import json


class JsonLineStoragePipeline(object):
    def __init__(self):
        self._file = None

    def on_crawler_started(self, crawler):
        path = crawler.settings.get('STORAGE_PATH', '')
        if not path:
            raise FileNotFoundError('missing config key: `STORAGE_PATH`')

        self._file = open(path, 'a+')

    def on_crawler_stopped(self, crawler):
        if self._file:
            self._file.close()

    def process_item(self, item, request, spider):
        if item and isinstance(item, dict):
            self._file.writeline(json.dumps(item))
