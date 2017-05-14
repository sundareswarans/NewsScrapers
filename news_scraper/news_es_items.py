from datetime import datetime
from elasticsearch_dsl import DocType, Date, String, Integer


class NewsDocType(DocType):
    """
    Document type to store in elastic cluster
    for indexing
    """
    id=String()
    title = String(analyzer='snowball')
    excerpt = String(analyzer='snowball')
    keywords = String(analyzer='keyword')
    author = String()
    publication_date = Date()
    created_at = Date()

    class Meta:
        index = 'news_index'

    @classmethod
    def from_item(cls, item, spider):
        return cls(title=item['title'],
                   excerpt=item['excerpt'],
                   keywords=item['keywords'],
                   author=item['author'],
                   publication_date=item['publication_date'],
                   # set the id of cache doc equal to
                   # id of mongo-db doc
                   meta={'id': spider.cache[item].upserted_id})

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super(NewsDocType, self).save(**kwargs)
