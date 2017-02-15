# -*- coding: utf-8 -*-

import os

def main():
    filename = os.path.join('ml-100k', 'u.item')
    delimiter = '|'

    with open(filename , 'r') as f:
        #first_line = f.readline()
        for i, line in enumerate(f):
            pieces = line.split(delimiter)

            # hard-coded
            item_id = pieces[0]
            imdb_url = pieces[4]
            print delimiter.join([item_id, imdb_url])
            #raw_input()

if __name__ == '__main__':
    main()