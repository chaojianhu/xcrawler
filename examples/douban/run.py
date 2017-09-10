"""
    main
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler import Crawler
from xcrawler.extensions.default_useragent import DefaultUserAgentExtension
from examples.douban.spiders.movie_info import DoubanMovieSpider


def main():
    settings = {
        'DOWNLOAD_TIMEOUT': 16,
        'DOWNLOAD_DELAY': .5,
        'CONCURRENT_REQUESTS': 10,
        'DEFAULT_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
                              'AppleWebKit/603.3.8 (KHTML, like Gecko) Version'
                              '/10.1.2 Safari/603.3.8',
        'INSTALLED_EXTENSIONS': [DefaultUserAgentExtension],
        'INSTALLED_PIPELINES': []

    }
    crawler = Crawler('DEBUG', **settings)
    crawler.crawl(DoubanMovieSpider)
    crawler.start()


if __name__ == '__main__':
    main()
