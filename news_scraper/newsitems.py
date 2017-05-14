"""
Defines Items for structured data, to be stored in
a database.
"""

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags, replace_entities


class NewsItem(scrapy.Item):
    """
    Structured data for storing the Author and an Article
    """
    # Author's name
    author = scrapy.Field(input_processor=MapCompose(lambda x: x.replace('NO-AUTHOR', '')),
                          output_processor=Join())
    
    # Description of the News Article
    title = scrapy.Field(input_processor=MapCompose(replace_entities, remove_tags),
                         output_processor=Join(),
                      )

    # Excerpt of the New Article
    excerpt = scrapy.Field(input_processor=MapCompose(replace_entities, remove_tags),
                            output_processor=Join(),
                      )

    # Source Link to the Article
    article_url = scrapy.Field(input_processor=TakeFirst())
    
    # Article
    article_text = scrapy.Field(input_processor=MapCompose(replace_entities, remove_tags),
                                output_processor=Join())

    # Keywords (tags) for search
    keywords = scrapy.Field(input_processor=MapCompose(lambda x: set(x.split(','))))

    # article publication date
    publication_date = scrapy.Field()

