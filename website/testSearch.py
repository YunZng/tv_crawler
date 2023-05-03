import re
from collections import Counter, defaultdict
from typing import Dict, List, NamedTuple

import numpy as np
from numpy.linalg import norm
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize


### File IO and processing

class Document(NamedTuple):
    doc_id: int
    title: List[str]
    actor: List[str]
    other: List[str]
    link: List[str]

    def sections(self):
        return [self.title, self.actor, self.other, self.link]

    def __repr__(self):
        return (f"doc_id: {self.doc_id}\n" +
            f"  title: {self.title}\n" +
            f"  actor: {self.actor}\n" +
            f"  other: {self.other}\n" +
            f"  link: {self.link}")


def read_stopwords(file):
    with open(file) as f:
        return set([x.strip() for x in f.readlines()])

stopwords = read_stopwords('common_words')

stemmer = SnowballStemmer('english')

def read_rels(file):
    rels = {}
    with open(file) as f:
        for line in f:
            qid, rel = line.strip().split()
            qid = int(qid)
            rel = int(rel)
            if qid not in rels:
                rels[qid] = []
            rels[qid].append(rel)
    return rels

def read_docs(file):
    docs = [defaultdict(list)]  # empty 0 index
    category = ''
    with open(file) as f:
        i = 0
        for line in f:
            line = line.strip()
            if line.startswith('.I'):
                i = int(line[3:])
                docs.append(defaultdict(list))
            elif re.match(r'\.\w', line):
                category = line[1]
            elif line != '':
                for word in word_tokenize(line):
                    docs[i][category].append(word.lower())

    return [Document(i + 1, d['T'], d['C'], d['O'], d['L'])
        for i, d in enumerate(docs[1:])]

def stem_doc(doc: Document):
    return Document(doc.doc_id, *[[stemmer.stem(word) for word in sec]
        for sec in doc.sections()])

def stem_docs(docs: List[Document]):
    return [stem_doc(doc) for doc in docs]

def remove_stopwords_doc(doc: Document):
    return Document(doc.doc_id, *[[word for word in sec if word not in stopwords]
        for sec in doc.sections()])

def remove_stopwords(docs: List[Document]):
    return [remove_stopwords_doc(doc) for doc in docs]


### Term-Document Matrix

class TermWeights(NamedTuple):
    title: float
    actor: float
    other: float
    link: float

def compute_doc_freqs(docs: List[Document]):
    freq = Counter()
    for doc in docs:
        words = set()
        for sec in doc.sections():
            for word in sec:
                words.add(word)
        for word in words:
            freq[word] += 1
    return freq

def compute_tf(doc: Document, doc_freqs: Dict[str, int], weights: list):
    vec = defaultdict(float)
    for word in doc.title:
        vec[word] += weights.title
    for word in doc.actor:
        vec[word] += weights.actor
    for word in doc.other:
        vec[word] += weights.other
    for word in doc.link:
        vec[word] += weights.link
    return dict(vec)  # convert back to a regular dict

def compute_tfidf(doc, doc_freqs, weights): # add one additional parameter N
    tf = compute_tf(doc, doc_freqs, weights)
    vec = defaultdict(float)
    for word in tf:
        if doc_freqs[word] == 0:
            vec[word] = 0
        else:
            vec[word] = tf[word] * (1 / doc_freqs[word])
    return dict(vec)  # convert back to a regular dict 


### Vector Similarity

def dictdot(x: Dict[str, float], y: Dict[str, float]):
    keys = list(x.keys()) if len(x) < len(y) else list(y.keys())
    return sum(x.get(key, 0) * y.get(key, 0) for key in keys)

def cosine_sim(x, y):
    num = dictdot(x, y)
    if num == 0:
        return 0
    return num / (norm(list(x.values())) * norm(list(y.values())))


### Precision/Recall

def interpolate(x1, y1, x2, y2, x):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m * x + b

def precision_at(recall: float, results: List[int], relevant: List[int]) -> float:
    p = [x / len(relevant) for x in range(1, len(relevant) + 1)]
    d = {k : v for v, k in enumerate(results)}
    relevant.sort(key = d.get)

    if recall == 0: 
        return 1
    elif recall not in p:
        prev = 0
        for post in p:
            if recall < post:
                if prev == post and len(p) > 1:
                    continue
                return interpolate(prev, precision_at(prev, results, relevant),
                                   post, precision_at(post, results, relevant), recall)
            else:
                prev = post

    idx = p.index(recall) + 1
    Rank_i = results.index(relevant[idx - 1]) + 1
    return idx / Rank_i

def mean_precision1(results, relevant):
    return (precision_at(0.25, results, relevant) +
        precision_at(0.5, results, relevant) +
        precision_at(0.75, results, relevant)) / 3

def mean_precision2(results, relevant):
    return sum(precision_at(i/10, results, relevant) for i in range(1, 11)) / 10

def norm_recall(results, relevant):
    rank_sum = 0
    for r in relevant:
        rank_sum += (results.index(r) + 1)
    
    i_sum = sum(range(1, len(relevant) + 1))

    return 1 - ((rank_sum - i_sum) / (len(relevant) * (len(results) - len(relevant))))

def norm_precision(results, relevant):
    rank_sum = 0
    for r in relevant:
        rank_sum += np.log(results.index(r) + 1)
    
    i_sum = 0
    for i in range(1, len(relevant) + 1):
        i_sum += np.log(i)

    N = len(results)
    R = len(relevant)
    denom = N * np.log(N) - (N - R) * np.log(N - R) - R * np.log(R)

    return 1 - ((rank_sum - i_sum) / denom)


### Search

def experiment():
    docs = read_docs('processRaw.raw')
    queries = read_docs('query.raw')
    rels = read_rels('query.rels')
    stopwords = read_stopwords('common_words')

    print('Links', 'p_0.25', 'p_0.5', 'p_0.75', 'p_1.0', 'p_mean1', 'p_mean2', 'r_norm', 'p_norm', sep='\t')

    processed_docs, processed_queries = process_docs_and_queries(docs, queries, True, True, stopwords)
    doc_freqs = compute_doc_freqs(processed_docs)
    doc_vectors = [compute_tfidf(doc, doc_freqs, TermWeights(title=4, actor=2, other=1, link=0)) for doc in processed_docs]

    metrics = []

    for query in processed_queries:
        query_vec = compute_tfidf(query, doc_freqs, TermWeights(title=4, actor=2, other=1, link=0))
        results = search(doc_vectors, query_vec)
        rel = rels[query.doc_id]

        metrics.append([
            precision_at(0.25, results, rel),
            precision_at(0.5, results, rel),
            precision_at(0.75, results, rel),
            precision_at(1.0, results, rel),
            mean_precision1(results, rel),
            mean_precision2(results, rel),
            norm_recall(results, rel),
            norm_precision(results, rel)
        ])

        averages = [f'{np.mean([metric[i] for metric in metrics]):.4f}'
            for i in range(len(metrics[0]))]
    
        for i in range(10):
            for doc in docs:
                if doc.doc_id == results[i]:
                    docLink = ''.join(doc.link)
                    print(''.join(doc.link), *averages, sep='\t')


def process_docs_and_queries(docs, queries, stem, removestop, stopwords):
    processed_docs = docs
    processed_queries = queries
    if removestop:
        processed_docs = remove_stopwords(processed_docs)
        processed_queries = remove_stopwords(processed_queries)
    if stem:
        processed_docs = stem_docs(processed_docs)
        processed_queries = stem_docs(processed_queries)
    return processed_docs, processed_queries


def search(doc_vectors, query_vec):
    results_with_score = [(doc_id + 1, cosine_sim(query_vec, doc_vec))
                    for doc_id, doc_vec in enumerate(doc_vectors)]
    results_with_score = sorted(results_with_score, key=lambda x: -x[1])
    results = [x[0] for x in results_with_score]
    return results


if __name__ == '__main__':
    experiment()