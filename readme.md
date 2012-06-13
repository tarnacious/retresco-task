Purpose
-------


This is my first effort at solving the following task in a job interview process. The task is as follows (I hope they don't mind me reproducing it here)

    One of our clients is doing some very strange stuff with Solr. What they want to do is to track each users visit on article pages and count the number of distinct visits per week, month and year.

    In order to do this with Solr, they add a new document to the index for each visit. This is stupid because they have some 55 million documents in Solr after 6 months already and it will only last for another 6 months until it will crash (at best).

    Instead of doing this with Solr I proposed to use Redis for that. If you don't know Redis, it is basically a data type server and not just an in memory key value store. Here are a few links:

    http://redis.io/topics/data-types-intro
    http://redis.io/documentation

    So if you could code (simple python proof of concept) just the methods of adding a new article, counting a visit for the last week/month/year for any article, retrieving those values and cleaning up the stuff each night. So the queries would be: give me the n most viewed articles yesterday, last week and this year.

    I am unsure if using bitmasks could help here but if you search for "redis bitmasks" or "redis count users" you'll find many usage examples.


Comments
--------

This solution has mostly just evolved as I played around with Redis setbit functions, but now does a lot of what the task requires and some it doesn't.

* It's currently Python 2 because I was having problems getting the Python Redis driver from PyPI to work with Python 3. I intend to update it to Python 3 when I get a chance.

* It has dependencies on redis-py and bitarray. (Does Python/pip have a Gemfile equivalent?)

* I haven't used much Python recently so it's probably not very idiomatic Python. I hope to update some of the names and use generators etc where possible.  

* This solution (using bitmasks to count unique visits) is only practical when you can my unique users into a tight keyspace.

* There may well be better ways to approach this problem, but the initial task description doesn't specify enough information to make that choice correctly. For example knowing rough numbers of unique documents, unique users and frequency of document visits and other analytics required would help influence the design and estimate memory usage etc. 

* I'm keen to hear any feedback.

