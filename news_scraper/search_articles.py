import os
import sys
import argparse
import json

from news_es_items import NewsDocType
from elasticsearch_dsl.connections import connections
from settings import ES_DEFAULT_HOST, MONGODB_DEFAULT_HOST
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
from bson.errors import InvalidId
from elasticsearch.exceptions import NotFoundError

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--search-field',
                        choices=('title', 'keywords', 'author', 'excerpt', ),
                        help='Field to use for search term. '
                        'default=%(default)s',
                        required=True)
    parser.add_argument('-s', '--search-term',
                        help='Term to search in the document. '
                        'default=%(default)s',
                        required=True)
    parser.add_argument('-l', '--limit',
                        help='Limit the number of results. '
                        'Default=%(default)s',
                        default=10)
    parser.add_argument('-d', '--dump-dir',
                        help='Destination directory to dump the'
                        'retrieved results. Default=%(default)s',
                        default='/tmp')

    args = parser.parse_args(argv)

    # establish a connection with elastic search
    es_client = connections.create_connection(hosts=[ES_DEFAULT_HOST], timeout=20)

    # create a search oject for the NewsDocType index
    es_search = NewsDocType.search().using(es_client)

    # frame the query
    es_search = es_search.query('match',
                               **{args.search_field: args.search_term})
    
    # run the search and process the results
    try:
        results = es_search.execute()
    except NotFoundError as e:
        print ('Search failed: %s' % e)
        return -1

    object_ids = []
    for obj in results:
        try:
            object_ids.append(ObjectId(str(obj.meta.id)))
        except InvalidId as e:
            print ('Igoring document with invalid-id: %s' % obj.meta.id)

    if not object_ids:
        print ('No records found for the given search term')
        return 0

    # Retrieve the documents from Mongo-DB
    mongo_client = MongoClient(MONGODB_DEFAULT_HOST)

    # articles DB
    db = mongo_client.articles

    # article collection
    articles = db.article

    # find all the objects that are of interest
    cursor = articles.find({"_id": {"$in": object_ids}})[:args.limit]

    # retrieve the documents and write them to the provided dump directory
    for document in cursor:
        document_path = os.path.join(args.dump_dir, str(document['_id']) + '.json')
        with open(document_path, 'w') as fout:
            print ('Writing document: %s' % document_path)
            fout.write(json_util.dumps(document))


if __name__ == '__main__':
    sys.exit(main())
