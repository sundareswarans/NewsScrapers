import os
import json
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from news_scraper.newsitems import NewsItem
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

READABILITY_URL = r"https://mercury.postlight.com/parser?url={}"


class NewsExtractSpider(scrapy.Spider):
    name = 'NewSpider'
    start_urls = ['https://www.theguardian.com']

    def __init__(self, readability_api_key=None, *args, **kwargs):
        super(NewsExtractSpider, self).__init__(*args, **kwargs)

        # fail immediately if readability api key is not provided as input
        if not readability_api_key:
            raise Exception('Readability API Key is missing. Unable to continue')
        self.readability_api_key = readability_api_key
        self.cache = {}
 
    def parse(self, response):
        """
        Parses the response and checks for links to article
        and yields Request to scrapy engine
        """
        selector = Selector(response) 

        # get all links to articles in this page.
        for article_link in selector.xpath(r'//a[@data-link-name="article"]'):

            # now request the news article page
            article_url = article_link.xpath('./@href').extract_first()
            
            readability_url = READABILITY_URL.format(article_url)
            
            request = Request(url=readability_url,
                              headers={'x-api-key': self.readability_api_key},
                              callback=self.parse_article)

            request.meta['src_article_url'] = article_url

            # yield the request, so that scrapy engine will
            # request the page concurrently at the background
            yield request

    def parse_article(self, response):
        """
        Parses the response for the Article, and extracts information
        about the author and article text.
        Yields a news item for the item pipeline to populate the DB
        Parses any links to Article in this page, if any.
        """
        json_response = json.loads(response.body_as_unicode())
        if json_response and all(k in json_response.keys()
                                 for k in {'title', 'excerpt', 
                                    'content', 'url', 'date_published'}):
            # retrieve the article contents from json data   
            news_item_loader = ItemLoader(item=NewsItem())
            article_url = json_response['url']

            news_item_loader.add_value('article_url', article_url)
            news_item_loader.add_value('article_text', json_response['content'])

            # load the information relevant to the new item (Article)
            news_item_loader.add_value('author', json_response['author'] or 'NO-AUTHOR')
            news_item_loader.add_value('title', json_response['title'])
            news_item_loader.add_value('excerpt', json_response['excerpt'])
            news_item_loader.add_value('publication_date', json_response['date_published'])

            # request the article page to collect any misc items
            request = Request(url=article_url,
                              callback=self.parse_articles_and_misc_items)

            # store the item loader for later use
            request.meta['news_item_loader'] = news_item_loader

            # request the article page
            yield request
        else:
            # request the article page (NOT in readability)
            # such that the response handler, will process
            # any additional links to articles in this page
            request = Request(url=response.meta['src_article_url'],
                              callback=self.parse_articles_and_misc_items)

            # request the article page
            yield request
 

    def parse_articles_and_misc_items(self, response):
        """
        Parses miscellaneous items like keywords etc, if responses' meta
        contains news item loader.
        Parse any additional articles links in this page and yields new
        request for each article links found
        """
        selector = Selector(response)
        if 'news_item_loader' in response.meta:
            news_item_loader = response.meta['news_item_loader']
            news_item_loader.add_value('author',
                selector.xpath('//meta[@name="author"]/@content').extract())
            news_item_loader.add_value('keywords',
                selector.xpath('//meta[@name="keywords"]/@content').extract_first())

            # yielding this item enters into the Pipeline stage
            yield news_item_loader.load_item()

        # process any additional article links in this page
        # and yield a request to process them
        for request in self.parse(response):
           yield request


    def closed(self, reason):
        pass
