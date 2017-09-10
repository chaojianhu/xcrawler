"""
    helpers
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""
from hashlib import sha1 as hash_method
from urllib.parse import urlparse, urlencode, urlunsplit
from urllib.error import URLError
from .errors import InvalidURLError

__all__ = ['url_fingerprint', 'safe_url', 'base_url',
           'run_hook_method', 'dict_keys_to_upper']


##################################
# Url helpers
##################################

def url_fingerprint(url):
    if url:
        h = hash_method()
        h.update(url.encode('utf-8'))
        return h.hexdigest()
    else:
        raise InvalidURLError()


def safe_url(url, remove_empty_query=True):
    if not url:
        raise InvalidURLError()

    try:
        scheme, netloc, path, params, query, fragment = urlparse(url)

        if not netloc and path:
            path, netloc = netloc, path

        queries = []
        for q in query.split('&'):
            if '=' not in q:
                break

            key, value = q.split('=')
            if remove_empty_query and not value:
                continue

            queries.append((key, value))
        queries.sort(key=lambda x: x[0])
        query = urlencode(queries)

        url = urlunsplit((scheme or 'http', netloc, path, query, fragment)).rstrip('/')
        return url
    except URLError:
        return url.rstrip('/')


def base_url(url):
    if not url:
        raise InvalidURLError()

    parser = urlparse(url)
    return '://'.join((parser.scheme or 'http', parser.netloc))


##################################
# Hooks
##################################

def run_hook_method(objs, method_name, *method_args, **method_kwargs):
    if not objs:
        return None

    for o in objs:
        method = getattr(o, method_name, None)
        if method and callable(method):
            method(*method_args, **method_kwargs)

    return None


##################################
# Misc
##################################

def dict_keys_to_upper(d):
    if not d:
        return {}
    try:
        return {k.upper(): v for k, v in d.items()}
    except AttributeError:
        return d
