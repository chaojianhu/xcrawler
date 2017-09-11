"""
    movie_info
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from bs4 import BeautifulSoup
from lxml import html
from xcrawler import BaseSpider, Request


class DoubanMovieSpider(BaseSpider):
    name = 'douban_movie'
    start_urls = [
        'https://movie.douban.com/tag/爱情',
        # 'https://movie.douban.com/tag/喜剧',
        # 'https://movie.douban.com/tag/动画',
        # 'https://movie.douban.com/tag/动作',
        # 'https://movie.douban.com/tag/史诗',
        # 'https://movie.douban.com/tag/犯罪'
    ]

    default_headers = {'Refer': 'https://movie.douban.com'}

    def start_requests(self):
        for req in super().start_requests():
            req.headers['Refer'] = 'https://movie.douban.com'
            yield req

    def parse(self, response):
        html_root = html.fromstring(response.content, base_url=response.base_url)

        for movie_url in html_root.xpath('//tr[@class="item"]/td/div/a/@href'):
            yield Request(movie_url, self,
                          cookies=response.cookies,
                          headers=self.default_headers,
                          callback=self.parse_movie_details)

        # Next page
        try:
            next_page_url = html_root.xpath('//span[@class="next"]/a/@href')[0]
        except IndexError:
            pass
        else:
            yield Request(next_page_url, self,
                          cookies=response.cookies,
                          headers=self.default_headers,
                          callback=self.parse)

    def parse_movie_details(self, response):
        html_root = html.fromstring(response.content,
                                    base_url=response.base_url)

        movie_info = dict()
        movie_info['片名'] = self.xpath_first(html_root,
                                            '//div[@id="content"]'
                                            '/h1/span[1]/text()').strip()

        # to pure text
        soup = BeautifulSoup(html.tostring(self.xpath_first(html_root,
                                                            '//div[@id="info"]')))
        for line in soup.get_text().splitlines():
            try:
                left, *right = line.split(':')
            except AttributeError:
                pass
            else:
                key = left.strip()
                value = ''.join(x.strip() for x in right)

                if key and value:
                    movie_info[key] = value

        yield movie_info

    @staticmethod
    def xpath_first(node, exp, default=''):
        try:
            return node.xpath(exp)[0]
        except IndexError:
            return default
