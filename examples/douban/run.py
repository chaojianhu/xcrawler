"""
    main
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler import Crawler
from xcrawler.extensions.default_useragent import DefaultUserAgentExtension
from examples.douban.spiders.movie_info import DoubanMovieSpider
from examples.douban.pipelines import JsonLineStoragePipeline


def main():
    settings = {
        'download_timeout': 16,
        'download_delay': .1,
        'concurrent_requests': 4,
        'storage_path': '/tmp/movie_details.jl',
        'default_user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
                              'AppleWebKit/603.3.8 (KHTML, like Gecko) Version'
                              '/10.1.2 Safari/603.3.8',
        'global_extensions': {0: DefaultUserAgentExtension},
        'global_pipelines': {0: JsonLineStoragePipeline}

    }
    crawler = Crawler('DEBUG', **settings)
    crawler.crawl(DoubanMovieSpider)
    crawler.start()


if __name__ == '__main__':
    main()
