"""
    news
    ~~~~~~~~~~~~~~

    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""
from lxml.html import fromstring

from xcrawler import BaseSpider, Request


class StackOverflowSpider(BaseSpider):
    name = 'stackoverflow'
    start_urls = ['http://stackoverflow.com/questions/tagged/python']

    def parse(self, response):
        root = fromstring(response.content, response.base_url)
        next_page_rule = '//a[@rel="next"]/@href'
        question_element_rule = '//div[@class="question-summary"]'

        next_url = response.urljoin(self.extract_first(root, next_page_rule))
        yield Request(next_url, self)

        for ele in root.xpath(question_element_rule):
            item = dict()
            item['question_title'] = self.extract_first(ele,
                                                        'div[@class="question-summary"]'
                                                        '/div[@class="summary"]/h3/a/text()')
            item['question_url'] = response.urljoin(self.extract_first(ele, 'a[@class="question-hyperlink"]/@href'))
            item['question_desc'] = self.extract_first(ele, 'div[@class="excerpt"]/text()').strip()
            item['question_tags'] = ele.xpath('a[@class="post-tag"]/text()')
            item['votes'] = self.extract_first(ele, 'span[@class="vote-count-post "]/strong/text()')
            item['username'] = self.extract_first(ele, 'div[@class="user-details"]/a/text()')
            yield item

    @staticmethod
    def extract_first(element, exp, default=''):
        r = element.xpath(exp)
        if len(r):
            return r[0]

        return default
