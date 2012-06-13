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


    def testDocumentRangeKeys(self):

        start_date = datetime(2012,6,12)
        end_date = datetime(2012,6,14)
        keys = self.keybuilder.document_range_keys("test_document", start_date, end_date)

        expected = ['views:test_document:2012:6:12', 
                    'views:test_document:2012:6:13',
                    'views:test_document:2012:6:14' ]
       
        self.assertEqual(expected, keys)
   

    def testAllDocumentPattern(self):

        keys = self.keybuilder.all_documents_pattern()
        
        expected = 'views:*:*:*:*'
        
        self.assertEqual(expected, keys)


class ViewCountTestCase(unittest.TestCase): 
    
    """
    
    Base test class for test the call into Redis.
    Sets up Redis and clears test keys.

    """

    def setUp(self):
        self.redis = redis.Redis()
        storage = bitmask_count.Storage(self.redis)
        self.article_views = bitmask_count.ArticleViews(storage) 
        
        self.deleteTestKeys()
    
    def tearDown(self):

        self.deleteTestKeys()
    
    def deleteTestKeys(self):
        test_keys = self.redis.keys("views:*")
        for key in test_keys:
            self.redis.delete(key)



class testCountingDailyDocumentViews(ViewCountTestCase):

    """
    
    Test viewing and counting unique views of a single document

    """


    def testEmptyKeyHasZeroViews(self):
        
        views = self.article_views.article_views("test_document", datetime(2012,6,12))

        self.assertEqual(0, views)


    def testOutOfRangeViews(self):
        
        # view article
        self.article_views.view_article("test_document", 1, datetime(2012,8,22))
        
        # get views
        views = self.article_views.article_views("test_document", datetime(2012,6,12))

        self.assertEqual(0, views)

    
    def testDifferentDocumentViews(self):
        
        # view article
        self.article_views.view_article("test_document_1", 1, datetime(2012,8,22))
        
        # get views
        views = self.article_views.article_views("test_document_2", datetime(2012,6,12))

        self.assertEqual(0, views)

    
    def testSingleView(self):
        
        # view article
        self.article_views.view_article("test_document", 1, datetime(2012,6,12))
        
        # get views
        views = self.article_views.article_views("test_document", datetime(2012,6,12))

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


class testCountMonthlyDocumentViews(ViewCountTestCase):

    """
    
    Test viewing and counting unique monthly views of a single document

    """

    def testMonthHasZeroViews(self):
        
        views = self.article_views.article_monthly_views("test_document", 6, 2012)

        self.assertEqual(0, views)
    
    
    def testOutOfRangeViews(self):
        
        # view article
        self.article_views.view_article("test_document", 1, datetime(2012,8,22))
        
        # get views
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


class testCountDateRangeDocumentViews(ViewCountTestCase):

    """
    
    Test viewing and counting unique views in a date range of a single document

    """

    def testRangeHasZeroViews(self):

        start_date = datetime(2012,6,12)
        end_date = datetime(2012,6,14)
        
        views = self.article_views.article_date_range_views("test_document", start_date, end_date)

        self.assertEqual(0, views)
    
    
    def testOutOfRangeViews(self):
        
        # view article
        self.article_views.view_article("test_document", 1, datetime(2012,6,22))

        # get views
        start_date = datetime(2012,6,12)
        end_date = datetime(2012,6,14)

        views = self.article_views.article_date_range_views("test_document", start_date, end_date)

        self.assertEqual(0, views)

    
    def testMultipleUniqueViews(self):
        
        # view article
        self.article_views.view_article("test_document", 1, datetime(2012,6,12))
        self.article_views.view_article("test_document", 5, datetime(2012,6,14))
        
        # get views
        start_date = datetime(2012,6,12)
        end_date = datetime(2012,6,14)

        views = self.article_views.article_date_range_views("test_document", start_date, end_date)

        self.assertEqual(2, views)

    
    def testDuplicateView(self):
        
        # view article
        self.article_views.view_article("test_document", 5, datetime(2012,6,12))
        self.article_views.view_article("test_document", 5, datetime(2012,6,14))
        
        # get views
        start_date = datetime(2012,6,12)
        end_date = datetime(2012,6,14)

        views = self.article_views.article_date_range_views("test_document", start_date, end_date)

        self.assertEqual(1, views)



class testAnalytics(ViewCountTestCase):

    """
    
    Test analytics

    """
    
    def setUp(self):

        ViewCountTestCase.setUp(self)
        
        self.analytics = bitmask_count.Analytics(self.article_views)


    def testReturnsAllUniqueArticles(self):

        self.article_views.view_article("a", 5, datetime(2012,6,12))
        self.article_views.view_article("a", 5, datetime(2012,6,14))
        self.article_views.view_article("a", 6, datetime(2012,6,14))
        self.article_views.view_article("b", 6, datetime(2012,4,14))
        self.article_views.view_article("c", 6, datetime(2012,6,14))
            
        all_articles = self.analytics.all_articles()
        
        self.assertEqual(sorted(["a","b","c"]), sorted(all_articles))


    def testDateRangeViews(self):
    
        self.article_views.view_article("a", 5, datetime(2012,6,12))
        self.article_views.view_article("a", 5, datetime(2012,6,14))
        self.article_views.view_article("a", 8, datetime(2012,6,14))
        self.article_views.view_article("a", 6, datetime(2012,6,14))
        
        self.article_views.view_article("c", 6, datetime(2012,4,14))
        self.article_views.view_article("c", 7, datetime(2012,4,14))

        self.article_views.view_article("b", 6, datetime(2012,6,14))

        most_views = self.analytics.date_range_views(datetime(2012,1,1),datetime(2013,1,1))

        self.assertEqual([("a",3),("c",2),("b",1)], most_views)


if __name__ == '__main__':

    unittest.main()
