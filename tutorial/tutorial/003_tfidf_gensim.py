# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities
import os
import utility_synopsis

#dir_path = 'movie_description/plot_summary'
#prefix = 'plot_summary'
dir_path = 'movie_description/synopsis'
prefix = 'synopsis'

id_filename_map = {}
for i, filename in enumerate(os.listdir(dir_path)):
    id_filename_map[i] = filename

def open_file_and_collect_all_text(path, filename):
    #print filename
    f = open(os.path.join(path, filename), 'r')
    content = ''.join(f.readlines())
    #print content
    f.close()
    return content

# test <START>
if False:
#if True:
    open_file_and_collect_all_text(dir_path, 'plot_summary-1580-tt0024252.txt')
    exit(0)
# <END>

# remove common words and tokenize
stoplist = set('for a an of the and to in'.split())


# memory-efficient dictionary construction <START>
from six import iteritems
# collect statistics about all tokens
#dictionary = corpora.Dictionary(line.lower().split() for line in open('mycorpus.txt'))
dictionary = corpora.Dictionary(open_file_and_collect_all_text(dir_path, filename).lower().split() for filename in os.listdir(dir_path))

# remove stop words and words that appear only once
stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
            if stopword in dictionary.token2id]
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
dictionary.filter_tokens(stop_ids + once_ids)  # remove stop words and words that appear only once
#dictionary.compactify()  # remove gaps in id sequence after words that were removed
dictionary.save('%s.dict' % (prefix))  # store the dictionary, for future reference
print(dictionary)
print(dictionary.token2id)
# <END>

# memory-efficient corpus construction <START>
class MyCorpus(object):
   def __iter__(self):
       #for line in open('mycorpus.txt'):
       #    # assume there's one document per line, tokens separated by whitespace
       #    yield dictionary.doc2bow(line.lower().split())
       for filename in os.listdir(dir_path):
           yield dictionary.doc2bow(open_file_and_collect_all_text(dir_path, filename).lower().split())

corpus_memory_friendly = MyCorpus()  # doesn't load the corpus into memory!
print(corpus_memory_friendly)
corpora.MmCorpus.serialize('%s.mm' % (prefix), corpus_memory_friendly)  # store to disk, for later use

for i, vector in enumerate(corpus_memory_friendly):  # load one vector into memory at a time
    if i > 10:
        break
    print(vector)
# <END>

# To actually convert tokenized documents to vectors:

#new_doc = "Human computer interaction"
new_doc = utility_synopsis.get_doc(0)
new_vec = dictionary.doc2bow(new_doc.lower().split())
print(new_vec)  # the word "interaction" does not appear in the dictionary and is ignored
#[(0, 1), (1, 1)]



# 
tfidf = models.TfidfModel(corpus_memory_friendly)

# To transform the whole corpus via TfIdf and index it, in preparation for similarity queries:
index = similarities.SparseMatrixSimilarity(tfidf[corpus_memory_friendly], num_features=30000)


sims = index[tfidf[new_vec]]

sims = sorted(enumerate(sims), key=lambda item: -item[1])
limit = 10
print(sims[:limit])
print([(id_filename_map[x[0]], x[1]) for x in sims[:limit]])

# check correctness
#>>> a1 = 0.7071067811865476
#>>> a0 = 0.7071067811865476
#>>> b0, b1, b2 = 0.5773502691896257,  0.5773502691896257, 0.5773502691896257
#
#print("tfidf representation of new_vec")
#print(tfidf[new_vec])
#print("tfidf representation of corpus")
#for vector in corpus_memory_friendly:  # load one vector into memory at a time
#     print(tfidf[vector])
#
#>>> import math
#>>> a1 * b2 / (math.sqrt(a0 ** 2 + a1 **2) * math.sqrt(b0 ** 2 + b1 ** 2 + b2 ** 2))
#0.408248290463863

