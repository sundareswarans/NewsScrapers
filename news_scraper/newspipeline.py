"""
Defines pipeline classes for transform and load stages
"""
import os
from pymongo import MongoClient
from collections import defaultdict
from pymongo.errors import DuplicateKeyError
import itertools


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
        keywords = set()
        for t in item['keywords']:
            keywords |= set(t.split(','))
        item['keywords'] = [k for k in keywords]
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
    authors_coll_name = 'author'

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
        # ensure author is added to DB, if not available
        try:
            self.authors.insert_one({ '_id': item['author'],
                                      'profile_url': item['author_profile_url'],
                                 })
        except (KeyError, DuplicateKeyError) as e:
            print ('Trying to insert an author with same name: %s' % e)
        else:
            print ('Author inserted successfully: %s' % item['author'])

        # add the article, and link the article with the author
        try:
            self.articles.insert_one({'_id': item['title'],
                                      'author_id': item['author'], # FK to Author
                                      'headline': item['headline'],
                                      'url': item['article_url'],
                                      'keywords': item['keywords'],
                                      'article': item['article_text'],
                                    })
        except (KeyError, DuplicateKeyError) as e:
            print ('Trying to insert an article with an existing title name: %s' % e)
        return item
  
