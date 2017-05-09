import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags


class NewsItem(scrapy.Item):

    default_output_processor = TakeFirst()

    author = scrapy.Field()
    
    author_profile_url = scrapy.Field()
    
    title = scrapy.Field(input_processor=MapCompose(remove_tags),
                         output_processor=Join(),
                      )
    headline = scrapy.Field(input_processor=MapCompose(remove_tags),
                            output_processor=Join(),
                      )    
    article_url = scrapy.Field()
    
    article_text = scrapy.Field(input_processor=MapCompose(remove_tags),
                                output_processor=Join(),
                      )
    keywords = scrapy.Field()

