"""
Defines pipeline classes for transform and load stages
"""
import os
from pymongo import MongoClient


class TransformPipeLine(object):

    def  process_item(self, item, spider):
	# removes empty lines in the article text
        item['article_text'] = ''.join([l for l in item['article_text'] if l.strip('\n')])
        keywords = set()
        for l in item['keywords']:
            keywords |= set(l.split(','))
        item['keywords'] = keywords
        item['article_url'] = item['article_url'][0]
        item['author'] = item['author'][0]
        item['author_profile_url'] = item['author_profile_url'][0]
        return item


NEWS_MONGO_DB_HOST_DEFAULT = r'mongodb://ssenthilvel:12345678@aws-ap-southeast-1-portal.2.dblayer.com:15386,aws-ap-southeast-1-portal.0.dblayer.com:15386/admin?ssl=true'

NEWS_MONGO_DB_HOST = os.getenv(r'NEWS_MONGO_DB_HOST', NEWS_MONGO_DB_HOST_DEFAULT)


class LoadPipeLine(object):

    article_collection_name = 'articles'

    def __init__(self, mongo_host_url=NEWS_MONGO_DB_HOST, mongo_db_name=None):
        self.mongo_url = mongo_host_url
        self.db_name = mongo_db_name

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_url)
        self.db = self.client[self.db_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.article_collection_name].insert(dict(item))
        return item
  
