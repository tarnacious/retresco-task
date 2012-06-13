import unittest
from datetime import datetime
import bitmask_count
import redis

class testKeys(unittest.TestCase):

    """
    
    Test the generation of keys

    """
    
    def setUp(self):

        self.keybuilder = bitmask_count.KeyBuilder()

    
    def testDocumentKey(self):

        date = datetime(2012,6,12)
        key = self.keybuilder.document_key("test_document", date) 

        expected = "views:test_document:2012:6:12"
       
        self.assertEqual(expected, key)
    
    
    def testDocumentMonthKey(self):

        key = self.keybuilder.document_month_key("test_document", 6, 2012) 

        expected = "views:test_document:2012:6:*"
       
        self.assertEqual(expected, key)



class testCountingDailyDocumentViews(unittest.TestCase):

    """
    
    Test viewing and counting unique views of a single document

    """

    def setUp(self):

        self.redis = redis.Redis()
        
        # Delete test keys
        test_keys = self.redis.keys("views:*")
        for key in test_keys:
            self.redis.delete(key)

        self.article_views = bitmask_count.ArticleViews(self.redis) 


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


class testCountMonthlyDocumentViews(unittest.TestCase):

    """
    
    Test viewing and counting unique views of a single document

    """

    def setUp(self):

        self.redis = redis.Redis()
        
        # Delete test keys
        test_keys = self.redis.keys("views:*")
        for key in test_keys:
            self.redis.delete(key)

        self.article_views = bitmask_count.ArticleViews(self.redis) 


    def testMonthHasZeroViews(self):
        
        date = datetime(2012,6,12)
        views = self.article_views.article_monthly_views("test_document", 6, 2012)

        self.assertEqual(0, views)
    

    def testMultipleUniqueViews(self):
        
        # view article
        self.article_views.view_article("test_document", 1, datetime(2012,6,12))
        self.article_views.view_article("test_document", 5, datetime(2012,6,14))
        
        # get views
        views = self.article_views.article_monthly_views("test_document", 6, 2012)

        self.assertEqual(2, views)

    
    def testDuplicateView(self):
        
        # view article
        self.article_views.view_article("test_document", 5, datetime(2012,6,12))
        self.article_views.view_article("test_document", 5, datetime(2012,6,14))
        
        # get views
        views = self.article_views.article_monthly_views("test_document", 6, 2012)

        self.assertEqual(1, views)



if __name__ == '__main__':

    unittest.main()
