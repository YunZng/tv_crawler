from flask import Blueprint, render_template, request
from .tv_crawler import run
from .search import *
import os

data_json = os.path.join(os.path.dirname(__file__), 'data.json')

views = Blueprint('views', __name__)

# pre-process files to save time
stopwords = read_stopwords()
stemmer = get_stemmer()
docs = read_json(data_json)
processed_docs = process_docs(docs, True, True, stopwords, stemmer)
doc_freqs = compute_doc_freqs(processed_docs)
doc_vectors = [compute_tfidf(doc, doc_freqs, TermWeights(title=4, actor=2, other=1)) for doc in processed_docs]

# the following func runs everytime we the route is opened, methods includes the type of acceptable requests
@views.route('/', methods=['GET', 'POST'])
def home():
    # get data from the post request
    title=''
    actor=''
    general=''
    results=[]
    show_result=False
    global docs, processed_docs, doc_freqs, doc_vectors
    if request.method == 'POST':
        data = request.form
        button = data.get('button')
        if button == 'search':
            title = data.get('title')
            actor = data.get('actor')
            general = data.get('general')
            show_result=True
            query = Document(-1, None, title.lower().split(), actor.lower().split(), general.lower().split())
            processed_query = process_docs([query], True, True, stopwords, stemmer)
            results = experiment(docs, processed_query, doc_freqs, doc_vectors)

        elif button == 'refresh':
            title = data.get('title')
            actor = data.get('actor')
            general = data.get('general')
            show_result=False
            run()
            docs = read_json(data_json)
            processed_docs = process_docs(docs, True, True, stopwords, stemmer)
            doc_freqs = compute_doc_freqs(processed_docs)
            doc_vectors = [compute_tfidf(doc, doc_freqs, TermWeights(title=4, actor=2, other=1)) for doc in processed_docs]

    # u can also pass variables in this function
    return render_template('home.html', title=title, actor=actor, general=general, results=results, show_result=show_result)

# This file is a blue print for our views, we need to register them in __init__.py