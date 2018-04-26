#File: featured_words_mod.py

import nltk
import praw
import pymysql
import sshtunnel
import time
import requests
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords, state_union, wordnet, movie_reviews
from nltk.stem import  PorterStemmer, WordNetLemmatizer
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.classify import ClassifierI
from statistics import mode

from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB

from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
import re
import pickle
import random

lister = [('https://www.orlandopetphotos.com', 1, 'neg', 0.8333333333333334), ('My fiancée and I run a photography photography photography photography business, check us out on Facebook! Memories By Milavetz', 1, 'neg', 0.8333333333333334)]


def process_tuples(data):
    processing_list = []
    final_list = []
    for tup in data:
        tokenized = nltk.word_tokenize(tup[0])
        for word in tokenized:
            all_lowercase = word.lower()
            no_special_char = re.sub(r'([^\sa-z])+', '', all_lowercase)
            processing_list.append(no_special_char)
    no_blanks = list(filter(None, processing_list))
    for lower_word in no_blanks:
        if lower_word not in stopwords.words('english'):
            final_list.append(lower_word)
    return final_list


def feature_words(data):
    words =  nltk.FreqDist(process_tuples(data))
    top_words = list(words.items())
    print(top_words)

feature_words(lister)

with open(output_pickle, 'wb') as handle:
    pickle.dump(filtered_words, handle, protocol=pickle.HIGHEST_PROTOCOL)
