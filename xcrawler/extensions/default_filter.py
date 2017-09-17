"""
    Extension: default_filter
    ~~~~~~~~~~~~~~

    Filter duplicate requests with simple hash container.

    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
from hashlib import md5

logger = logging.getLogger(__name__)


class DefaultRequestFilterExtension(object):
    def __init__(self):
        self._seen = set()

    def process_request(self, request, spider):
        if request is None:
            return None

        if request.method.upper() != 'GET':
            # Do not cache non-GET request
            return request

        fp = self.request_fingerprint(request)
        if fp in self._seen:
            # Just drop this request
            logger.debug('Drop duplicate request: {}'.format(request))
            return None

        self._seen.add(fp)
        return request

    @staticmethod
    def request_fingerprint(req):
        return md5(str(req).encode('utf-8')).hexdigest()
