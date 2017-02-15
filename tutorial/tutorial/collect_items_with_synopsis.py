# -*- coding: utf-8 -*-

import os
import sqlite3

def collect_files_with_prefix(prefix):
    item_ids = []
    cnt = 0
    for x in os.listdir('.'):
        if 0 == x.find(prefix):
            cnt += 1
            #print x

            left = x.find('-')
            right = x.rfind('-')
            item_id = x[left + 1: right]
            item_ids.append(item_id)
        #break
    print 'cnt:', cnt
    return item_ids

def main():
    cx = sqlite3.connect(os.path.join('spiders', 'my_db.db'))
    cur = cx.cursor()

    #
    ret = collect_files_with_prefix('synopsis-')
    for item_id in ret:
        cur.execute("insert into items_with_synopsis (item_id) values (%s);" % (item_id))
        cx.commit()
    
    ret = collect_files_with_prefix('plot_summary-')
    for item_id in ret:
        cur.execute("insert into items_with_plot_summary (item_id) values (%s);" % (item_id))
        cx.commit()

    cur.close()

if __name__ == '__main__':
    main()