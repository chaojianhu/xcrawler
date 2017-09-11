"""
    news
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""
from lxml import html

from xcrawler import BaseSpider, Request


class BaiduNewsSpider(BaseSpider):
    name = 'baidu_news'
    start_urls = ['http://news.baidu.com/']

    def parse(self, response):
        root = html.fromstring(response.content, base_url=response.base_url)
        for element in root.xpath('//a[@target="_blank"]'):
            title = self.extract_first(element, 'text()')
            link = self.extract_first(element, '@href').strip()
            if title:
                if link.startswith('http://') or link.startswith('https://'):
                    yield {'title': title, 'link': link}
                    yield Request(link, self,
                                  callback=self.parse_news,
                                  meta={'title': title})

    def parse_news(self, response):
        print(response)

    @staticmethod
    def extract_first(element, exp, default=''):
        r = element.xpath(exp)
        if len(r):
            return r[0]

        return default
