BOT_NAME = 'NEWS-SCRAPER'

SPIDER_MODULES = ['news_scraper.newspider']
NEWSPIDER_MODULE = 'news_scraper.newspider'

ITEM_PIPELINES = {
   'news_scraper.newspipeline.FilterPipeLine': 100,
   'news_scraper.newspipeline.TransformPipeLine': 300,
   'news_scraper.newspipeline.LoadPipeLine': 800,
   'news_scraper.newspipeline.IndexDocumentInElasticsearchPipeLine': 900,
}
ES_DEFAULT_HOST = 'https://ssenthilvel:12345678@portal131-1.superior-elasticsearch-news-27.personal-227.composedb.com:15387/'
LOG_LEVEL = 'DEBUG'

