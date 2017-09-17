"""
    test_extensions
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler.extensions.default_useragent import DefaultUserAgentExtension
from xcrawler.extensions.default_filter import DefaultRequestFilterExtension


def test_default_useragent_extension():
    class Crawler(object):
        settings = {
            'DEFAULT_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
                                  'AppleWebKit/603.3.8 (KHTML, like Gecko) Version'
                                  '/10.1.2 Safari/603.3.8'
        }

    ext = DefaultUserAgentExtension()
    crawler = Crawler()

    ext.on_crawler_started(crawler)
    assert ext.user_agent == crawler.settings['DEFAULT_USER_AGENT']

    assert ext.process_request(None, None) is None

    class Request(object):
        def __init__(self):
            self.headers = {}

    assert "User-Agent" in ext.process_request(Request(), None).headers
    ext.user_agent = None
    assert 'User-Agent' not in ext.process_request(Request(), None).headers

    req = Request()
    req.headers['User-Agent'] = 'User-Agent'
    assert ext.process_request(
        req, None).headers['User-Agent'] == 'User-Agent'


def test_default_filter_extension():
    ext = DefaultRequestFilterExtension()

    from xcrawler.http import Request

    class FakeSpider:
        name = 'fake_spider'

        def parse(self):
            pass

    # GET request
    req = Request('http://foo.example/1?query=bar1', FakeSpider())
    assert ext.process_request(req, req.spider) is req
    assert ext.process_request(req, req.spider) is None

    req2 = Request('http://foo.example/1?query=bar2', FakeSpider())
    assert ext.process_request(req2, req2.spider) is req2

    # POST request
    req3 = Request('http://foo.example/login', FakeSpider(), method='POST')
    assert ext.process_request(req3, req3.spider) is req3
    assert ext.process_request(req3, req3.spider) is req3
    assert ext.process_request(req3, req3.spider) is req3
