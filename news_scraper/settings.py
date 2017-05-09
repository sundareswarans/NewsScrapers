

BOT_NAME = 'NEWS-SCRAPER'

SPIDER_MODULES = ['news_scraper.newspider']
NEWSPIDER_MODULE = 'news_scraper.newspider'

ITEM_PIPELINES = {
    'news_scraper.newspipeline.TransformPipeLine': 300,
    #'news_scraper.newspipeline.LoadPipeLine': 800,
}

LOG_LEVEL = 'DEBUG'


