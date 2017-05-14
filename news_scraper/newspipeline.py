"""
Defines pipeline classes for transform and load stages
"""
import os
from collections import defaultdict
import itertools

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from scrapy.exceptions import DropItem
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from news_scraper.newsitems import NewsItem
from news_scraper.news_es_items import NewsDocType


from elasticsearch_dsl.connections import connections

import settings


class FilterPipeLine(object):
    """
    First level filter to remove the items that doesn't contains
    article_text, author, and related details
    """
    EXPECTED_FIELDS = set(NewsItem.__dict__['fields'].keys())
    def process_item(self, item, spider):
        """
        Allows the item to be processed in the pipeline, if all the 
        relevant fields are present.
        Else, the item is dropped.
        """
        if all (k in self.EXPECTED_FIELDS for k in item.keys()):
            # allow this item to be processed in the pipeline
            return item
        # stop processing this item from processing in the pipeline
        print ('Dropping item: %r' % str(item))
        raise DropItem('Dropping item due to missing fields.')


class TransformPipeLine(object):
    """
    This pipe-line accpets an NewsItem and transforms it
    by removing unwanted lines in article text, and 
    """
    def  process_item(self, item, spider):
        """
        Processes an News item, and cleanses the items
        """
	    # Remove all the empty lines.
        text = [txt
	            for txt in item['article_text'].split('\n')
	            if txt.rstrip('\n')
	           ]
        item['article_text'] = ''.join(text)
        return item


# NOTE: We are using SSL connection for connecting to the MongoDB
# The CA certificate needs to be installed in the host where we run the client
#
NEWS_MONGO_DB_HOST_DEFAULT = r'mongodb://ssenthilvel:12345678@aws-ap-southeast-1-portal.2.dblayer.com:15386/articles?ssl=true'
NEWS_MONGO_DB_HOST = os.getenv(r'NEWS_MONGO_DB_HOST', NEWS_MONGO_DB_HOST_DEFAULT)


class LoadPipeLine(object):
    """
    Load pipeline loads authors and articles into
    MongoDB.
    DB Name: articles
         + Collections:
                   + author  (PK)
                   + article (FK)
    """
    articles_db_name = 'articles'
    articles_coll_name = 'article'

    def __init__(self, mongo_host_url=NEWS_MONGO_DB_HOST, mongo_db_name='articles'):
        self.mongo_url = mongo_host_url
        self.db_name = mongo_db_name

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_url)
        
        # articles database
        self.db = self.client[self.db_name]
        
        # author and article collections
        self.authors = self.db.author
        self.articles = self.db.article

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # ensure article is added to DB.
        try:
            update_result = self.articles.update_one(
                {'title': item['title']}, # filter
                {"$set": { # document
                  'title': item['title'],
                  'author': item['author'],
                  'excerpt': item['excerpt'],
                  'url': item['article_url'],
                  'article': item['article_text'],
                  'title': item['title'],
                  'publication_date': item['publication_date'],
                  'keywords': item['keywords']}
                }, upsert=True)

            # store the update result in the cache for later use
            spider.cache[item] = update_result

        except DuplicateKeyError as e:
            print ('Trying to insert an article with an existing title name: %s' % e)
        except KeyError as e:
            msg = 'KeyError while inserting article to mongodb: %s. For item: %s' % (e, str(item))
            print (msg)
        return item


class IndexDocumentInElasticsearchPipeLine(object):
    """
    Pipeline item, that writes the given item to
    elastic search DB for indexing and searching the information
    """
    def __init__(self, es_host=None, es_port=None, index_name=None, doc_type=None):
        self.es_host = es_host or settings.ES_DEFAULT_HOST
        self.index_name = index_name or 'articles'
        self.doc_type = doc_type or NewsDocType

    def open_spider(self, spider):
        self.es_client = connections.create_connection(hosts=[self.es_host], timeout=20)
        self.search = Search(using=self.es_client, index=self.index_name, doc_type=self.doc_type)

    def process_item(self, item, spider):
        try:
            if item in spider.cache:
                # save the items to the elastic search index DB
                self.doc_type.from_item(item, spider).save()
        except (AttributeError) as e:
            print ('Error while insering to Elasticsearch: %s' % e)
        return item
