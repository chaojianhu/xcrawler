xcrawler, a light-weight web crawler framework
------------------------

# Introduction
[xcrawler](https://github.com/ChrisLeeGit/xcrawler), it's a light-weight web crawler framework. Some of its design concepts are borrowed from the well-known framework [Scrapy](https://github.com/scrapy).
I'm very interested in web crawling, however, I'm just a newbie to web scraping. I did this so that I can learn more basics of web crawling and Python language.

![arch](http://blog.chriscabin.com/wp-content/uploads/2017/09/xcrawler-arch.png)

# Features
- Simple: extremely easy to customize your own spider;
- Fast: multiple requests are spawned concurrently with the threading-downloader or gevent-downloader;
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


```
class BaiduNewsSpider(BaseSpider):
    name = 'baidu_news_spider'
    start_urls = ['http://news.baidu.com/']
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'
    }

    def spider_started(self):
        self.file = open('items.jl', 'w')

    def spider_stopped(self):
        self.file.close()

    def spider_idle(self):
        # you can add new requests to the engine
        print('I am in idle mode')
        # self.crawler.crawl(new_request, spider=self)

    def make_requests_from_url(self, url):
        return Request(url, headers=self.default_headers)

    def parse(self, response):
        root = fromstring(response.content, base_url=response.base_url)
        for element in root.xpath('//a[@target="_blank"]'):
            title = self._extract_first(element, 'text()')
            link = self._extract_first(element, '@href').strip()
            if title:
                if link.startswith('http://') or link.startswith('https://'):
                    yield {'title': title, 'link': link}
                    yield Request(link, headers=self.default_headers, callback=self.parse_news,
                                  meta={'title': title})

    def parse_news(self, response):
        pass

    def process_item(self, item):
        print(item)
        print(json.dumps(item, ensure_ascii=False), file=self.file)

    @staticmethod
    def _extract_first(element, exp, default=''):
        r = element.xpath(exp)
        if len(r):
            return r[0]

        return default


def main():
    settings = {
        'download_delay': 1,
        'download_timeout': 6,
        'retry_on_timeout': True,
        'concurrent_requests': 16,
        'queue_size': 512
    }
    crawler = CrawlerProcess(settings, 'DEBUG')
    crawler.crawl(BaiduNewsSpider)
    crawler.start()

main()
```

- ![log](http://blog.chriscabin.com/wp-content/uploads/2016/12/working.png)

- ![results](http://blog.chriscabin.com/wp-content/uploads/2016/12/results.png)

# License
[xcrawler](https://github.com/ChrisLeeGit/xcrawler) is licensed under the MIT license, please feel free and happy crawling!

