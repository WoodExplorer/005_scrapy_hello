# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities


documents = ["Human machine interface for lab abc computer applications",
             "A survey of user opinion of computer system response time",
             "The EPS user interface management system",
             "System and human system engineering testing of EPS",
             "Relation of user perceived response time to error measurement",
             "The generation of random binary unordered trees",
             "The intersection graph of paths in trees",
             "Graph minors IV Widths of trees and well quasi ordering",
             "Graph minors A survey"]


# remove common words and tokenize
stoplist = set('for a of the and to in'.split())
texts = [[word for word in document.lower().split() if word not in stoplist]
         for document in documents]

# remove words that appear only once
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

texts = [[token for token in text if frequency[token] > 1]
         for text in texts]

from pprint import pprint  # pretty-printer
pprint(texts)
#[['human', 'interface', 'computer'],
# ['survey', 'user', 'computer', 'system', 'response', 'time'],
# ['eps', 'user', 'interface', 'system'],
# ['system', 'human', 'system', 'eps'],
# ['user', 'response', 'time'],
# ['trees'],
# ['graph', 'trees'],
# ['graph', 'minors', 'trees'],
# ['graph', 'minors', 'survey']]


dictionary = corpora.Dictionary(texts)
dictionary.save('deerwester.dict')  # store the dictionary, for future reference
print(dictionary)

print(dictionary.token2id)


# To actually convert tokenized documents to vectors:

new_doc = "Human computer interaction"
new_vec = dictionary.doc2bow(new_doc.lower().split())
print(new_vec)  # the word "interaction" does not appear in the dictionary and is ignored
#[(0, 1), (1, 1)]


corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)  # store to disk, for later use
print(corpus)
for vector in corpus:
     print(vector)
###########################

tfidf = models.TfidfModel(corpus)

vec = [(0, 1), (4, 1)]
print(tfidf[vec])

index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=12)

sims = index[tfidf[vec]]
print(list(enumerate(sims)))
