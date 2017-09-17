"""
    test_helpers
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import pytest
from xcrawler.errors import InvalidURLError
from xcrawler.helpers import (url_fingerprint, safe_url, base_url,
                              run_hook_method, dict_keys_to_upper)


def test_url_fingerprint():
    with pytest.raises(InvalidURLError):
        _ = url_fingerprint('')

    assert url_fingerprint('http://www.baidu.com') == '633a42441e296c9004a78ab' \
                                                      'e0b2ee3b37559d32f'
    assert url_fingerprint('https://www.baidu.com') == '354abe0fccb2fb8cf553b6' \
                                                       'eef2ce24b2f3db80d1'


def test_safe_url():
    with pytest.raises(InvalidURLError):
        _ = safe_url('')

    assert safe_url('http://www.baidu.com') == 'http://www.baidu.com'
    assert safe_url('http://www.baidu.com/') == 'http://www.baidu.com'
    assert safe_url('www.baidu.com/') == 'http://www.baidu.com'
    assert safe_url('https://www.baidu.com') == 'https://www.baidu.com'
    assert safe_url('http://www.baidu.com?q=foo&p=bar') == 'http://www.baidu.com?p=bar&q=foo'
    assert safe_url('http://www.baidu.com?q=a&p=&m=hello') == 'http://www.baidu.com?m=hello&q=a'


def test_base_url():
    with pytest.raises(InvalidURLError):
        _ = base_url('')

    assert base_url('http://www.baidu.com/foo/bar?q=david&p=maria') == 'http://www.baidu.com'
    assert base_url('https://www.baidu.com/foo/bar?q=david&p=maria') == 'https://www.baidu.com'


def test_run_hook_method():
    assert run_hook_method(None, 'fake_method') is None
    assert run_hook_method([], 'fake_method') is None

    class Foo(object):
        def __init__(self):
            self.message = None

        def fake_method(self, msg):
            self.message = msg

    foo = Foo()
    run_hook_method([foo], 'no_such_method', 'hello, world')
    assert foo.message is None

    run_hook_method([foo], 'fake_method', 'hello, world')
    assert foo.message == 'hello, world'


def test_dict_keys_to_upper():
    assert dict_keys_to_upper(None) is None
    assert dict_keys_to_upper([1, 3, 4]) == [1, 3, 4]
    assert dict_keys_to_upper({}) == {}
    assert dict_keys_to_upper({1: 'foo', 2: 'bar'}) == {1: 'foo', 2: 'bar'}
    assert dict_keys_to_upper({'foo': 'foo', 'bar': 'bar'}) == {'FOO': 'foo', 'BAR': 'bar'}
