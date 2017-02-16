# -*- coding: utf-8 -*-

import os
import sqlite3


def main():
    #
    file_path = os.path.join(os.path.join('spiders', 'ml-100k'), 'u.data')
    delimiter = '\t'

    tuples = []
    with open(file_path, 'r') as f:
        #first_line = f.readline()
        for i, line in enumerate(f):
            #print line
            pieces = line.split(delimiter)
            
            if (4 != len(pieces)):
                print i
                assert(4 == len(pieces))

            tuples.append(tuple([int(x) for x in pieces]))
    #exit(0)

    ##
    cx = sqlite3.connect(os.path.join('spiders', 'my_db.db'))
    cur = cx.cursor()

    #
    cur.execute("select distinct(item_id) from items_with_synopsis;")
    all_distinct_items_ids = cur.fetchall()
    all_distinct_items_ids = [x[0] for x in all_distinct_items_ids]
    print 'count: %d' % (len(all_distinct_items_ids))
    
    cur.close()

    ### step 3: filter
    tuples = filter(lambda x: x[1] in all_distinct_items_ids, tuples)

    ### step 4:
    file_path += '.filtered'
    with open(file_path, 'w') as f:
        for t in tuples:
            f.write(delimiter.join([str(x) for x in t]) + '\n')

if __name__ == '__main__':
    main()