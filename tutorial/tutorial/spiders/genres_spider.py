# -*- coding: utf-8 -*-

import scrapy
import os
import codecs
import sqlite3

class SynopsisOrLongestPlotSummarySpider(scrapy.Spider):
    """ This spider will:
        Crawl genres of items whose ids appear in the items_with_synopsis table in the sqlite database
        and save these genres into the genres_of_items_with_synopsis table.
    """
    name = "genre"
    cx = sqlite3.connect(os.path.join('spiders', 'my_db.db'))

    def start_requests(self):

        #
        #self.log_file = open('as_log.txt', 'a+')
        #self.log_file.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        #
        #

        input_file = os.path.join('spiders', 'ml-100k-imdb-urls.txt')
        delimiter = '|'

        tuples = []
        with open(input_file , 'r') as f:
            #first_line = f.readline()
            for i, line in enumerate(f):
                pieces = line.split(delimiter)
                item_id = pieces[0].strip()
                url = pieces[1].strip() # hard-coded

                if len(url) < 2:
                    continue

                tuples.append((item_id, url))

        self.log('len(tuples): %d' % len(tuples))
        # 
        cur = self.cx.cursor()
        cur.execute('select distinct(item_id) from items_with_synopsis')
        items_with_synopsis = cur.fetchall()
        items_with_synopsis = [x[0] for x in items_with_synopsis]
        cur.close()

        items_with_synopsis = set(items_with_synopsis)
        self.log("len(items_with_synopsis): %d" % len(items_with_synopsis))
        tuples = filter(lambda x: int(x[0]) in items_with_synopsis, tuples)
        self.log('len(tuples): %d' % len(tuples))
        
        #
        # For some reasons unknown, the program failed to crawl the genres of the following items.
        # I manually set tuples, crawled their genres and commented the corresponding statment.
        #tuples = [('268', 'http://us.imdb.com/M/title-exact?Chasing+Amy+(1997)'), 
#('1003', 'http://us.imdb.com/M/title-exact?That%20Darn%20Cat%20(1997)'), ]

        ###
        #limit = 1
        limit = 50000000
        cnt = 0
        cur = self.cx.cursor()
        #tuples = [('1003', 'http://us.imdb.com/M/title-exact?That%20Darn%20Cat%20(1997)')]
        for i, (item_id, url) in enumerate(tuples):
            if cnt > limit:
            #if i > limit:
                break

            yield scrapy.Request(url=url, callback=lambda response, item_id=item_id:self.parse(response, item_id))
            cnt += 1
        cur.close()

    def parse(self, response, item_id):
        genre_list = [x.strip() for x in response.xpath("//div[@itemprop='genre']/a/text()").extract()]
        self.log("genre_list: %s" % (genre_list))

        self.crawler.stats.inc_value('aa_status/parse_count')
        if 0 == len(genre_list):
            self.crawler.stats.inc_value('downloader/genre_list__empty')

        #
        genres = ','.join(genre_list)
        cur = self.cx.cursor()
        #cur.execute("insert or replace into item2page (item_id, page_id) values ('%s', '%s');" % (item_id, page_id))
        cur.execute("insert into genres_of_items_with_synopsis (item_id, genres) values (%s, '%s');" % (item_id, genres))
        self.cx.commit()
        cur.close()
        #
