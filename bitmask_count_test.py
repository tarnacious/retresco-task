import unittest
from datetime import datetime
import bitmask_count
import redis

class testbitmask_count(unittest.TestCase):

    def setUp(self):

        self.redis = redis.Redis()
        
        # Delete test keys
        test_keys = self.redis.keys("views:*")
        for key in test_keys:
            self.redis.delete(key)

        self.article_views = bitmask_count.ArticleViews(self.redis) 


    def testDocumentKey(self):

        date = datetime(2012,6,12)
        key = self.article_views.document_key("test_document", date) 

        expected = "views:test_document:2012:6:12"
       
        self.assertEqual(expected, key)


    def testEmptyKeyHasZeroViews(self):
        
        date = datetime(2012,6,12)
        views = self.article_views.article_views("test_document", date)

        self.assertEqual(0, views)

    def testSingleView(self):
        
        date = datetime(2012,6,12)
        
        # view article
        self.article_views.view_article("test_document", 1, date)
        
        # get views
        views = self.article_views.article_views("test_document", date)

        self.assertEqual(1, views)
    
    
    def testDuplicateView(self):
        
        date = datetime(2012,6,12)
        
        # view article
        self.article_views.view_article("test_document", 1, date)
        self.article_views.view_article("test_document", 1, date)
        
        # get views
        views = self.article_views.article_views("test_document", date)

        self.assertEqual(1, views)

    
    def testMultipleUniqueViews(self):
        
        date = datetime(2012,6,12)
        
        # view article
        self.article_views.view_article("test_document", 1, date)
        self.article_views.view_article("test_document", 5, date)
        
        # get views
        views = self.article_views.article_views("test_document", date)

        self.assertEqual(2, views)

if __name__ == '__main__':

    unittest.main()
