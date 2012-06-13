from redis import Redis
from bitarray import bitarray
from datetime import datetime
from datetime import timedelta

class KeyBuilder:
    
    def __init__(self):

        self.key_format = "views:%(document_name)s:%(year)s:%(month)s:%(day)s"
    
    
    def document_key(self, document_name, date):

        key_values = { "document_name": document_name,
                       "day": str(date.day),
                       "month": str(date.month),
                       "year": str(date.year) }
        
        return self.key_format % key_values

    
    def document_month_key(self, document_name, month, year):
        
        key_values = { "document_name": document_name,
                       "day": "*",
                       "month": str(month),
                       "year": str(year) }
        
        return self.key_format % key_values
    

    def document_range_keys(self, document_name, date_from, date_to):

        # additional day to make the range inclusive, hack?
        number_of_days = (date_to - date_from).days + 1

        days = [date_from + timedelta(days = i) for i in range(number_of_days)]

        def key_values(date):

            return  { "document_name": document_name,
                      "day": str(date.day),
                      "month": str(date.month),
                      "year": str(date.year) }
        
        return [self.key_format % key_values(day) for day in days]


    def all_documents_pattern(self):

        key_values = { "document_name": "*",
                       "day": "*",
                       "month": "*",
                       "year": "*" }
        
        return self.key_format % key_values


class Storage:

    def __init__(self, redis):

        self.redis = redis


    def all_keys(self, key_patterns):

        keys = []

        if isinstance(key_patterns, list):
            for document_key in key_patterns:
                keys.extend(self.redis.keys(document_key)) 
        else:
            keys = self.redis.keys(key_patterns)

        return keys


    def mark_viewed(self, document_key, user_key):
        
        self.redis.setbit(document_key, user_key, 1)


    def count_views(self, document_key_patterns): 
       
        keys = self.all_keys(document_key_patterns)        

        union = bitarray()
        
        for key in keys:

            key_value = self.redis.get(key)

            if not key_value == None:
                bits = bitarray() 
                bits.frombytes(key_value)

                if bits.length() > union.length():
                    union.extend(list(0 for n in range(bits.length() - union.length())))
                union = union | bits 
               
        return union.count()



class ArticleViews:

    def __init__(self, storage):

        self.storage = storage
        self.keybuilder = KeyBuilder()

    def view_article(self, document_name, user_key, date):

        key = self.keybuilder.document_key(document_name, date)
        self.storage.mark_viewed(key, user_key)

    def article_views(self, document_name, date):

        key = self.keybuilder.document_key(document_name, date)

        return self.storage.count_views(key)

    
    def article_monthly_views(self, document_name, month, year):

        key = self.keybuilder.document_month_key(document_name, month, year)

        return self.storage.count_views(key)


    def article_daterange_views(self, document_name, start_date, end_date):

        key = self.keybuilder.document_range_keys(document_name, start_date, end_date)

        return self.storage.count_views(key)


    def all_articles(self):
        pattern = self.keybuilder.all_documents_pattern()
        all_keys = self.storage.all_keys(pattern)

        all_document_names = [full_key.split(":")[1] for full_key in all_keys]

        unique_document_names = set(all_document_names)

        return list(unique_document_names)



