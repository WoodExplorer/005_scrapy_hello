# -*- coding: utf-8 -*-

import scrapy
import os
import codecs
import sqlite3

class SynopsisFor1MSpider(scrapy.Spider):
    """ This spider will:
        (1) read urls from a file containing imdb url for movieLens movies.
        (2) visit the urls and find out page ids for those movies.
        (3) visit synopsis pages of those movies with url constructed from page ids.
        (4) if a movie does not have a synopsis, under current implementation, we can 
            only find this out at this point, and the spider will resort to plot plot summary 
            pages and save longest plot summaries as substitute.
    """
    name = "synopsis_for_1M"
    cx = sqlite3.connect(os.path.join('spiders', 'my_db_1m.db'))

    def start_requests(self):

        #
        #self.log_file = open('as_log.txt', 'a+')
        #self.log_file.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        #
        #

        input_file, delimiter = os.path.join(os.path.join('spiders', 'ml-1m'), 'movies.dat'), '::'

        tuples = []


        cur = self.cx.cursor()
        cur.execute('select max(item_id) from item2page')
        r = cur.fetchone()
        biggest_item_id = r[0]
        self.log('biggest_item_id: %d' % biggest_item_id)


        with open(input_file , 'r') as f:
            #first_line = f.readline()
            for i, line in enumerate(f):
                pieces = line.split(delimiter)
                item_id = pieces[0].strip()
                title = pieces[1].strip() # hard-coded

                #if len(url) < 2:
                #    continue

                if (int(item_id) < biggest_item_id):
                    pass
                else:
                    tuples.append((item_id, title))

        self.log('len(tuples): %d' % len(tuples))
        # 
        # 
        
        #
        #limit = 3
        limit = 50000000
        cnt = 0
        #tuples = [('1003', 'http://us.imdb.com/M/title-exact?That%20Darn%20Cat%20(1997)')]
        for i, (item_id, title) in enumerate(tuples):
            if cnt > limit:
            #if i > limit:
                break

            #if item_id < biggest_item_id:
            #    self.log('pass item_id:%s' % (item_id))
            #    continue

            cur.execute('select count(*) from item2page where item_id = %s' % (item_id))
            r = cur.fetchone()
            if 1 == r[0]:
                self.log('pass item_id:%s' % (item_id))
                pass
            else:
                self.log('processing item_id:%s' % (item_id))
                url = 'http://www.imdb.com/M/title-exact?' + title
                yield scrapy.Request(url=url, callback=lambda response, item_id=item_id:self.parse(response, item_id))
                cnt += 1
        cur.close()

    def parse(self, response, item_id):
        signal_page_id_list_empty = 0
        signal_page_id_list_too_big = 0

        page_id_list = response.xpath("//meta[@property='pageId']/@content").extract()
        if 0 == len(page_id_list):
            signal_page_id_list_empty += 1
            return
        if 1 < len(page_id_list):
            signal_page_id_list_too_big += 1
            return

        page_id = page_id_list[0]
        # construct url for synopsis
        url_for_synopsis_template = "http://www.imdb.com/title/%s/synopsis"
        url_for_synopsis = url_for_synopsis_template % page_id

        #
        cur = self.cx.cursor()
        #cur.execute("insert or replace into item2page (item_id, page_id) values ('%s', '%s');" % (item_id, page_id))
        cur.execute("insert into item2page (item_id, page_id) values (%s, '%s');" % (item_id, page_id))
        self.cx.commit()
        cur.close()
        #

        yield scrapy.Request(url=url_for_synopsis, callback=lambda response, item_id=item_id, pageid=page_id: self.parse_synopsis_page(response, item_id, page_id))

    def parse_synopsis_page(self, response, item_id, page_id):
        signal_synopsis_list_empty = 0
        signal_synopsis_list_too_big = 0

        # This is the list containing html element for synopsis.
        # There should be only one such html element.
        synopsis_list = response.xpath("//div[@id='swiki.2.1']") 
        
        if 0 == len(synopsis_list):
            signal_synopsis_list_empty += 1
            return
        if 1 < len(synopsis_list):
            signal_synopsis_list_too_big += 1
            return

        synopsis = synopsis_list[0]
        synopsis = synopsis.xpath('text()').extract()
        synopsis = '\n\n'.join(synopsis)

        if 10 >= len(synopsis):
            url_for_plot_summary_template = 'http://www.imdb.com/title/%s/plotsummary'
            url_for_plot_summary = url_for_plot_summary_template % page_id
            yield scrapy.Request(url=url_for_plot_summary, callback=lambda response, item_id=item_id, pageid=page_id: self.parse_plot_summary_page(response, item_id, page_id))
            return

        filename = 'synopsis-%s-%s.txt' % (item_id, page_id)
        #with open(filename, 'wb') as f:
        #    f.write(synopsis)
        f = codecs.open(filename, "wb", "utf-8")
        f.write(synopsis)
        f.close()

        self.log('Saved file %s' % filename)

    def parse_plot_summary_page(self, response, item_id, page_id):
        signal_plot_summary_list_empty = 0
        signal_plot_summary_list_too_big = 0

        # This is the list containing html element for synopsis.
        # There should be only one such html element.
        plot_summary_list = response.xpath("//p[@class='plotSummary']") 
        
        if 0 == len(plot_summary_list):
            plot_summary_list_empty += 1
            return
        # No, there could be multiple plot summaries
        #if 1 < len(plot_summary_list):
        #    plot_summary_list_too_big += 1
        #    return

        plot_summary_list = ['\n\n'.join(x.xpath('text()').extract()) for x in plot_summary_list] # pay attention to the join
        plot_summary_list_len = [len(x) for x in plot_summary_list]
        max_len = max(plot_summary_list_len)
        plot_summary_list = filter(lambda x: len(x) == max_len, plot_summary_list)
        assert(len(plot_summary_list) > 0)
        plot_summary = plot_summary_list[0]

        #
        filename = 'plot_summary-%s-%s.txt' % (item_id, page_id)
        #with open(filename, 'wb') as f:
        #    f.write(synopsis)
        f = codecs.open(filename, "wb", "utf-8")
        f.write(plot_summary)
        f.close()

        self.log('Saved file %s' % filename)        
