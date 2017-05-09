import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from news_scraper.newsitems import NewsItem
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags


class NewsExtractSpider(scrapy.Spider):
    name = 'NewSpider'
    start_urls = ['https://www.theguardian.com']

    def parse(self, response):
        """
        Parses the response and checks for links to article
        and yields Request to scrapy engine
        """
        xps = HtmlXPathSelector(response)
        # get all links to articles in this page.
        for article_link in xps.select(r'//a[@data-link-name="article"]'):
            # prepare news item loader for this link
            # and populate with known information
            news_item_loader = ItemLoader(item=NewsItem())

            article_url = article_link.select('./@href').extract_first()
            news_item_loader.add_value('article_url', article_url)

	    # now request the news article page
            request = Request(url=article_url,
                              callback=self.parse_article)

            request.meta['news_item_loader'] = news_item_loader

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
        # get XPath selector and the news item loader
        # and update the news item
        xps = HtmlXPathSelector(response)
        news_item_loader = response.meta['news_item_loader']

        # load the information relevant to the new item (Article)
        news_item_loader.add_value('author', xps.select(r'//meta[@name="author"]/@content').extract_first())
        news_item_loader.add_value('author_profile_url', xps.select(r'//a[@rel="author"]/@href').extract())
        news_item_loader.add_value('title', xps.select(r'/html/head/title/text()').extract())
        news_item_loader.add_value('headline', xps.select(r'//meta[@name="description"]/@content').extract())
        news_item_loader.add_value('keywords', xps.select(r'//meta[@name="keywords"]/@content').extract())
        news_item_loader.add_value('article_text', xps.select(r'//article[@id="article"]').extract())

        # process this news item through the pipeline processor
        yield news_item_loader.load_item()

        # parse any additional link to articles
        return self.parse(response)

    def closed(self, reason):
        pass
