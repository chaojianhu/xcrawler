"""
    test_extensions
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler.extensions.default_useragent import DefaultUserAgentExtension
from xcrawler.extensions.default_filter import DefaultRequestFilterExtension
from xcrawler.extensions.retry import RetryRequestExtension


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


def test_retry_request_extension():
    class Crawler(object):
        settings = {
            'RETRY_ENABLED': True,
            'RETRY_ON_TIMEOUT': True,
            'RETRY_ON_CONNECTION_ERROR': True,
            'RETRY_ON_STATUS_CODE': {400, 403, 404, 503},
            'MAX_TRIES': 1
        }

    ext = RetryRequestExtension()

    crawler = Crawler()
    ext.on_crawler_started(crawler)

    # check settings are ok
    assert ext.retry_enabled is True
    assert ext.retry_on_timeout is True
    assert ext.retry_on_connection_error is True
    assert ext.retry_on_status_code == {400, 403, 404, 503}
    assert ext.max_tries == 1

    from xcrawler.errors import (HTTPTimeoutError,
                                 HTTPConnectionError,
                                 HTTPStatusError)
    from xcrawler.http import Request, Response

    url = 'http://foo.example.com'

    class FakeSpider:
        name = 'fake_spider'

        def parse(self): pass

    request = lambda: Request(url, FakeSpider())

    # retry on timeout
    req = request()

    assert ext.process_http_error(HTTPTimeoutError(), None,
                                  req, req.spider) is req
    assert req.retry_count == 1

    # max retry count exceeds, cannot retry that again.
    assert ext.process_http_error(HTTPTimeoutError(), None,
                                  req, req.spider) is None

    # retry on connection error
    req1 = request()
    assert ext.process_http_error(HTTPConnectionError(), None,
                                  req1, req1.spider) is req1
    assert req1.retry_count == 1

    # retry on http status error
    req2 = request()
    resp1 = Response(req2.url, 400, b'content', 'utf-8',
                     req2, reason='Bad request')
    assert ext.process_http_error(HTTPStatusError(), resp1,
                                  resp1.request, None) is req2
    assert req2.retry_count == 1
