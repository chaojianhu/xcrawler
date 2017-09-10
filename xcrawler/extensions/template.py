"""
    template
    ~~~~~~~~~~~~~~

    Extension template

    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""


class FooExtension(object):
    def __init__(self):
        pass

    def on_crawler_started(self, crawler):
        pass

    def on_crawler_stopped(self, crawler):
        pass

    def on_spider_started(self, spider):
        pass

    def on_spider_stopped(self, spider):
        pass

    def on_spider_idle(self, spider):
        pass

    def process_request(self, request, spider):
        pass

    def process_response(self, response, request, spider):
        pass

    def process_http_error(self, error, response, request, spider):
        pass
