"""
    test_crawler
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import pytest
from xcrawler.crawler import Crawler
from xcrawler.errors import InvalidExtensionError, InvalidPipelineError


def test_crawler_initial_status():
    crawler = Crawler()
    assert crawler.spider_extensions == []
    assert crawler.global_extensions == []
    assert crawler.spider_pipelines == []
    assert crawler.global_pipelines == []
    assert list(crawler.spiders) == []


def test_crawler_add_extensions():
    crawler = Crawler()

    class InvalidExtension(object):
        pass

    with pytest.raises(InvalidExtensionError):
        crawler.add_global_extension(InvalidExtension, 0)
        crawler.add_spider_extension(InvalidExtension, 0, 'foo')
        crawler.add_spider_extension(None, 0, 'foo')
        crawler.global_extensions(None, 0)

    class ValidExtension(object):
        def process_request(self, *args):
            pass

    crawler.add_global_extension(ValidExtension, 0)
    assert len(crawler.global_extensions) == 1
    assert isinstance(crawler.global_extensions[0], ValidExtension)

    crawler.add_spider_extension(ValidExtension, 0, 'foo')
    assert len(crawler.spider_extensions) == 1
    assert isinstance(crawler.spider_extensions[0], ValidExtension)
    assert len(crawler.spider_extensions_by_name('foo')) == 1
    assert isinstance(crawler.spider_extensions_by_name('foo')[0], ValidExtension)


def test_crawler_add_pipeline():
    crawler = Crawler()

    class InvalidPipeline(object):
        pass

    with pytest.raises(InvalidPipelineError):
        crawler.add_global_pipeline(InvalidPipeline, 0)
        crawler.add_spider_pipeline(InvalidPipeline, 0, 'bar')
        crawler.add_global_pipeline(None, 0)
        crawler.add_spider_pipeline(None, 0, 'foo')

    class ValidPipeline(object):
        def process_item(self, *args, **kwargs):
            pass

    crawler.add_global_pipeline(ValidPipeline, 0)
    assert len(crawler.global_pipelines) == 1
    assert isinstance(crawler.global_pipelines[0], ValidPipeline)

    crawler.add_spider_pipeline(ValidPipeline, 0, 'bar')
    assert len(crawler.spider_pipelines) == 1
    assert isinstance(crawler.spider_pipelines[0], ValidPipeline)
    assert isinstance(crawler.spider_pipelines_by_name('bar')[0], ValidPipeline)
