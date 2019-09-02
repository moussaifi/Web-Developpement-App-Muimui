# pip install psycopg2-binary
# pip install -U gensim
# sudo rm -f /etc/boto.cfg
# pip install google-compute-engine
# Run imports with nltk.download('punkt') for the first time

import pandas as pd
from gensim.models import Doc2Vec
from sklearn import utils
import gensim
import re
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from sklearn.feature_extraction import stop_words
import string
import psycopg2
import sys
import nltk
# nltk.download('punkt')


fname_model = "muimui_doc2vec_model"
host = "dbinstance.c6phnxzyppjs.us-west-2.rds.amazonaws.com"
dbname = "muimui"
username = "marwa"
password = "muimuidb"
port = "5432"

sql_conn_string = "host='{}' dbname='{}' user='{}' \
                   password='{}' port='{}'".format(host, dbname,
                                                   username,
                                                   password, port)


def cleanText(text):
    """
    Remove html elements, convert to lower
    """
    text = BeautifulSoup(text, "lxml").text
    text = re.sub(r'\|\|\|', r' ', text)
    text = re.sub(r'http\S+', r'<URL>', text)
    text = text.lower()
    text = text.replace('x', '')
    return text


def clean_text(text):
    """
    Tokenize text and return a non-unique list of tokenized words
    found in the text. Normalize to lowercase, strip punctuation,
    remove stop words, drop words of length < 3, strip digits.
    """
    stops = list(stop_words.ENGLISH_STOP_WORDS)
    text = text.lower()
    regex = re.compile('[' + re.escape(string.punctuation) + '0-9\\r\\t\\n]')
    # delete stuff but leave at least a space to avoid clumping together
    nopunct = regex.sub(" ", text)
    words = nopunct.split(" ")
    # ignore a, an, to, at, be, ...
    words = [w for w in words if (len(w) > 2 and (w not in stops))]
    words = ' '.join(words)
    return words


def tokenize_text(text):
    """
    tokenize sentence and remove words with less than 2 characters
    """
    tokens = []
    for sent in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sent):
            if len(word) < 2:
                continue
            tokens.append(word.lower())
    return tokens


def retrieve_imglinks(sql_conn_string, ID_list):
    """
    Returns images links from db for the
    NN from doc2vec model
    """
    conn = psycopg2.connect(sql_conn_string)
    cur = conn.cursor()
    tuples = tuple(ID_list)
    cmds = [f"""
            select ID,image_link from products
            where ID in {tuples}
            ;
            """]
    out_collection = {}
    for c in cmds:
        try:
            cur.execute(c)
            rows = cur.fetchall()
            for ID, data in rows:
                out_collection[ID] = data
            conn.commit()
        except psycopg2.ProgrammingError:
            print("""CAUTION FAILED: '%s' """ % c)
            conn.rollback()
    return [out_collection[ID] for ID in tuples]

def return_nn(text):
    input_query = text
    input_query = tokenize_text(clean_text(cleanText(input_query)))
    model_load = Doc2Vec.load(fname_model)
    vec = model_load.infer_vector(input_query)
    ID_list = [ID for ID,
               score in model_load.docvecs.most_similar([vec], topn=100)]
    
    return ID_list

# if __name__ == '__main__':
#     input_query = sys.argv[1]
#     input_query = tokenize_text(clean_text(cleanText(input_query)))
#     model_load = Doc2Vec.load(fname_model)
#     vec = model_load.infer_vector(input_query)
#     ID_list = [ID for ID,
#                score in model_load.docvecs.most_similar([vec], topn=10)]
#     img_links = retrieve_imglinks(sql_conn_string, ID_list)
#     for il in img_links:
#         print(il)
