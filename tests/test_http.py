"""
    test_http
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler.http.request import Request
from xcrawler.http.response import Response


class Spider:
    name = 'foo_spider'


spider = Spider()


def test_request_object_repr():
    req = Request('http://www.baidu.com', spider)
    assert repr(req) == "<[foo_spider]Request GET 'http://www.baidu.com'>"


def test_response_object():
    req = Request('http://www.foo.com', spider, callback='parse_foo')
    resp = Response('http://www.foo.com',
                    200, b'<html><head><title>Hello, world</title></head></html>',
                    'utf-8', req)
    assert repr(resp) == "<[foo_spider]Response 'http://www.foo.com': 200>"
    assert resp.callback == 'parse_foo'
    assert resp.text == '<html><head><title>Hello, world</title></head></html>'
    assert resp.decode_content('ascii') == '<html><head><title>Hello, world' \
                                           '</title></head></html>'
