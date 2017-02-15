# -*- coding: utf-8 -*-

import scrapy
import os
import codecs


class SynopsisOrLongestPlotSummarySpider(scrapy.Spider):
    """ This spider will:
        (1) read urls from a file containing imdb url for movieLens movies.
        (2) visit the urls and find out page ids for those movies.
        (3) visit synopsis pages of those movies with url constructed from page ids.
        (4) if a movie does not have a synopsis, under current implementation, we can 
            only find this out at this point, and the spider will resort to plot plot summary 
            pages and save longest plot summaries as substitute.
    """
    name = "synopsis"

    def start_requests(self):

        #
        #self.log_file = open('as_log.txt', 'a+')
        #self.log_file.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        #
        #

        input_file = os.path.join('spiders', 'ml-100k-imdb-urls.txt')
        delimiter = '|'

        urls = []
        with open(input_file , 'r') as f:
            #first_line = f.readline()
            for i, line in enumerate(f):
                pieces = line.split(delimiter)
                url = pieces[1].strip() # hard-coded

                urls.append(url)

        # 
        limit = 5
        for i, url in enumerate(urls):
            if i > limit:
                break
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
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

        yield scrapy.Request(url=url_for_synopsis, callback=lambda response, pageid=page_id: self.parse_synopsis_page(response, page_id))

    def parse_synopsis_page(self, response, page_id):
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
            yield scrapy.Request(url=url_for_plot_summary, callback=lambda response, pageid=page_id: self.parse_plot_summary_page(response, page_id))
            return

        filename = 'synopsis-%s.txt' % page_id
        #with open(filename, 'wb') as f:
        #    f.write(synopsis)
        f = codecs.open(filename, "wb", "utf-8")
        f.write(synopsis)
        f.close()

        self.log('Saved file %s' % filename)

    def parse_plot_summary_page(self, response, page_id):
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
        filename = 'plot_summary-%s.txt' % page_id
        #with open(filename, 'wb') as f:
        #    f.write(synopsis)
        f = codecs.open(filename, "wb", "utf-8")
        f.write(plot_summary)
        f.close()

        self.log('Saved file %s' % filename)        
