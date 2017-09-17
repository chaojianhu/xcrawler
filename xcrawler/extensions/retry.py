"""
    retry
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
from ..errors import HTTPStatusError, HTTPTimeoutError, HTTPConnectionError

logger = logging.getLogger(__name__)


class RetryRequestExtension(object):
    def __init__(self):
        self.retry_enabled = False
        self.max_tries = 3
        self.retry_on_timeout = False
        self.retry_on_connection_error = False
        self.retry_on_status_code = {400}

    def on_crawler_started(self, crawler):
        self.retry_enabled = crawler.settings.get('RETRY_ENABLED', False)
        self.max_tries = crawler.settings.get('MAX_TRIES', 3)
        self.retry_on_timeout = crawler.settings.get('RETRY_ON_TIMEOUT', False)
        self.retry_on_connection_error = crawler.settings.get('RETRY_ON_CONNECTION_ERROR', False)

        for code in crawler.settings.get('RETRY_ON_STATUS_CODE', []):
            self.retry_on_status_code.add(code)

    def process_http_error(self, error, response, request, spider):
        if self.retry_enabled is False:
            return None

        if isinstance(error, HTTPTimeoutError) and self.retry_on_timeout and \
                request and request.retry_count < self.max_tries:
            request.retry_count += 1
            logger.debug('Retry request {!r}: download time out error'
                         ' happened'.format(request))
            return request

        if isinstance(error, HTTPStatusError) and self.retry_on_status_code \
                and response and response.status in self.retry_on_status_code \
                and request and request.retry_count < self.max_tries:
            request.retry_count += 1
            logger.debug('Retry request {!r}: error status code {} '
                         'found'.format(request, response.status))
            return request

        if isinstance(error, HTTPConnectionError) and \
                self.retry_on_connection_error and \
                request and request.retry_count < self.max_tries:
            request.retry_count += 1
            logger.debug('Retry request {!r}: connection error '
                         'happened'.format(request))
            return request
