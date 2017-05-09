"""
Defines Items for structured data, to be stored in
a database.
"""

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags


class NewsItem(scrapy.Item):
    """
    Structured data for storing the Author and an Article
    """
    # Author's name
    author = scrapy.Field(output_processor=TakeFirst())
    
    # Author's profile URL
    author_profile_url = scrapy.Field(output_processor=Join())
    
    # Description of the News Article
    title = scrapy.Field(input_processor=MapCompose(remove_tags),
                         output_processor=Join(),
                      )

    # Headline of the New Article
    headline = scrapy.Field(input_processor=MapCompose(remove_tags),
                            output_processor=Join(),
                      )

    # Source Link to the Article
    article_url = scrapy.Field()
    
    # Article
    article_text = scrapy.Field(input_processor=MapCompose(remove_tags),
                                output_processor=Join(),
                      )

    # Keywords (tags) for search
    keywords = scrapy.Field(ouput_processor=Join())

