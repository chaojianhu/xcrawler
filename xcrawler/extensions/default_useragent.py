"""
    default_useragent
    ~~~~~~~~~~~~~~

    Add a default user-agent to the requests.

    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging

logger = logging.getLogger(__name__)


class DefaultUserAgentExtension(object):
    config_key = 'DEFAULT_USER_AGENT'

    def __init__(self):
        self._user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) ' \
                           'AppleWebKit/603.3.8 (KHTML, like Gecko) Version' \
                           '/10.1.2 Safari/603.3.8'

    def crawler_started(self, crawler):
        if self.config_key in crawler.settings:
            self._user_agent = crawler.settings[self.config_key]

    def process_request(self, request, spider):
        if not request or 'User-Agent' in request.headers or not self._user_agent:
            return request

        logger.debug('[{}]{} adds default user agent: '
                     '{!r}'.format(spider, request, self._user_agent))
        request.headers['User-Agent'] = self._user_agent
        return request
