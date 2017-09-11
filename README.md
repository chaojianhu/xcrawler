A light-weight web crawler framework: xcrawler
------------------------

[![Build Status](https://www.travis-ci.org/0xE8551CCB/xcrawler.svg?branch=feature-refactor-architecture)](https://www.travis-ci.org/0xE8551CCB/xcrawler)

# Introduction
[xcrawler](https://github.com/ChrisLeeGit/xcrawler), it's a light-weight web crawler framework. Some of its design concepts are borrowed from the well-known framework [Scrapy](https://github.com/scrapy).
I'm very interested in web crawling, however, I'm just a newbie to web scraping. I did this so that I can learn more basics of web crawling and Python language.

![arch](http://blog.chriscabin.com/wp-content/uploads/2017/09/xcrawler-arch.png)

# Features
- Simple: extremely easy to customize your own spider;
- Fast: multiple requests are spawned concurrently with the `ThreadPoolDownloader` or `ProcessPoolDownloader`;
- Flexible: different scheduling strategies are provided -- FIFO/FILO/Priority based;
- Extensible: write your own extensions to make your crawler much more powerful.

# Install
1. create a virtual environment for your project, then activate it:


    ```
    virtualenv crawlenv
    source crawlenv/bin/activate
    ```

1. download and install this package:

    ```
    pip install git+https://github.com/0xE8551CCB/xcrawler.git
    ```

# Quick start
1. Define your own spider:

    ```
    from xcrawler import BaseSpider


    class DoubanMovieSpider(BaseSpider):
        name = 'douban_movie'
        custom_settings = {}
        start_urls = ['https://movie.douban.com']

        def parse(self, response):
            # extract items from response
            # yield new requests
            # yield new items
            pass
    ```

1. Define your own extension:

    ```
    class DefaultUserAgentExtension(object):
        config_key = 'DEFAULT_USER_AGENT'

        def __init__(self):
            self._user_agent = ''

        def on_crawler_started(self, crawler):
            if self.config_key in crawler.settings:
                self._user_agent = crawler.settings[self.config_key]

        def process_request(self, request, spider):
            if not request or 'User-Agent' in request.headers or not self._user_agent:
                return request

            logger.debug('[{}]{} adds default user agent: '
                         '{!r}'.format(spider, request, self._user_agent))
            request.headers['User-Agent'] = self._user_agent
            return request
    ```

1. Define a pipeline to store scraped items:

    ```
    class JsonLineStoragePipeline(object):
        def __init__(self):
            self._file = None

        def on_crawler_started(self, crawler):
            path = crawler.settings.get('STORAGE_PATH', '')
            if not path:
                raise FileNotFoundError('missing config key: `STORAGE_PATH`')

            self._file = open(path, 'a+')

        def on_crawler_stopped(self, crawler):
            if self._file:
                self._file.close()

        def process_item(self, item, request, spider):
            if item and isinstance(item, dict):
                self._file.writeline(json.dumps(item))
    ```

1. Config the crawler:

    ```
    settings = {
            'download_timeout': 16,
            'download_delay': .5,
            'concurrent_requests': 10,
            'storage_path': '/tmp/hello.jl',
            'default_user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
                                  'AppleWebKit/603.3.8 (KHTML, like Gecko) Version'
                                  '/10.1.2 Safari/603.3.8',
            'global_extensions': {0: DefaultUserAgentExtension},
            'global_pipelines': {0: JsonLineStoragePipeline}

        }
    crawler = Crawler('DEBUG', **settings)
    crawler.crawl(DoubanMovieSpider)
    ```

1. Bingo, you are ready to go now:

    ```
    crawler.start()
    ```


# License
[xcrawler](https://github.com/ChrisLeeGit/xcrawler) is licensed under the MIT license, please feel free and happy crawling!

