from redis import Redis
from bitarray import bitarray

class ArticleViews:

    def __init__(self, redis):

        self.redis = redis


    def document_key(self, document_name, date):

        key_format = "views:%(document_name)s:%(year)d:%(month)d:%(day)d"
        
        key_values = { "document_name": document_name,
                       "day": date.day,
                       "month": date.month,
                       "year": date.year }
        
        return key_format % key_values


    def view_article(self, document_name, user_key, date):

        key = self.document_key(document_name, date)

        self.redis.setbit(key, user_key, 1)


    def article_views(self, document_name, date):

        key = self.document_key(document_name, date)

        key_value = self.redis.get(key)

        if key_value == None:
            return 0

        bits = bitarray() 
        bits.frombytes(key_value)
        return bits.count()

