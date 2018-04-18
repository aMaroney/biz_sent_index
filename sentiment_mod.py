#File: sentiment_mod.py

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

import pickle
import random

print('nltk version: ',nltk.__version__)

class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for classifier_features in self._classifiers:
            vote = classifier_features.classify(features)
            votes.append(vote)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for confidence_features in self._classifiers:
            vote = confidence_features.classify(features)
            votes.append(vote)

        choice_votes = votes.count(mode(votes))
        certainty = choice_votes/len(votes)
        return certainty


# positive = open('positive.txt', 'r', encoding="ISO-8859-1", errors='replace').read()
# negative = open('negative.txt', 'r', encoding="ISO-8859-1", errors='replace').read()

'''
a list containing tuples of a sentence and it's positive or negative sentiment
('the rock is destined to be the 21st century's new " conan " and that he's going to make a splash... ', 'pos'),
'''
# documents = []

pickle_load_documents = open('documents.pickle', 'rb')
documents = pickle.load(pickle_load_documents)
pickle_load_documents.close()

'''
all words (positive and negative) tokenized in a list
['the', 'rock', 'is', 'destined', 'to', 'be', 'the', '21st', 'century',...
'''
pickle_load_all_words = open('all_words.pickle', 'rb')
all_words = pickle.load(pickle_load_all_words)
pickle_load_all_words.close()

# all_words = []


#  j is adject, r is adverb, and v is verb
# allowed_word_types = ["J","R","V"]
# allowed_word_types = ["J"]
#
# for p in positive.split('\n'):
#     documents.append((p, "pos"))
#     words = word_tokenize(p)
#     pos = nltk.pos_tag(words)
#     for w in pos:
#         if w[1][0] in allowed_word_types:
#             all_words.append(w[0].lower())
#
# for p in negative.split('\n'):
#     documents.append((p, "neg"))
#     words = word_tokenize(p)
#     pos = nltk.pos_tag(words)
#     for w in pos:
#         if w[1][0] in allowed_word_types:
#             all_words.append(w[0].lower())
#
# pickle_ise = open('documents.pickle', 'wb')
# pickle.dump(documents, pickle_ise)
# pickle_ise.close()

# write_out = open('document.txt', 'w')
# write_out.writelines(str(documents))
# write_out.close()

# write_out = open('all_words.txt', 'w')
# write_out.writelines(str(all_words))
# write_out.close()

'''
all_words frequency distribution looks like [('film', 1590), ('with', 1564), ('this', 1443), ('for', 1437), ('its', 1338), ('movie', 1336)]
'''
#taking the 5,000 most used words
#frequency distribution that tells us the frequency of each vocabulary item in all_words_dict.
# all_words = nltk.FreqDist(all_words)
# print(all_words.most_common(3))
# print(all_words['settles'])

# pickle_ise_all_words = open('all_words.pickle', 'wb')
# pickle.dump(all_words, pickle_ise_all_words)
# pickle_ise_all_words.close()

# featured_words = list(all_words.keys())[:5000]

# pickle_ise_featured_words = open('featured_words.pickle', 'wb')
# pickle.dump(featured_words, pickle_ise_featured_words)
# pickle_ise_featured_words.close()

pickle_ise_featured_words = open('featured_words.pickle', 'rb')
featured_words = pickle.load(pickle_ise_featured_words)
pickle_ise_featured_words.close()

def find_features(document):
    words = word_tokenize(document)
    features = {}
    for w in featured_words:
        # passing into the dictionary the 'w'/'word pulled from documents via iteration as the dict key and a True or False boolean as the value
        #checking to see if any of the featured_words are in the rev
        features[w] = (w in words)

    # write_out = open('features.txt', 'w')
    # write_out.writelines(str(features))
    # write_out.close()

    # the feature variable looks like this: {'proceed': False, 'deserve': False, 'butterflies': False,... '
    return features

'''
appending the featuresets list with True or False based on in the find_features functions above, which checks if words in featured_words
are in the single review 'rev'. The second thing appended to the list is the pos or neg string that's
in the documents. So you end up with a list containing a dictionary of the words checked against as the key and the True or False
as the value in position [0] (i.e. the 'features' variable) and the pos or neg in position [1].
({'cliff': False, 'non-mystery': False, 'patronising': False, 'bong': False}, 'pos')
'''

###a 'one-liner' to create the feature set.
featuresets = [(find_features(rev), category) for (rev, category) in documents]

'''
we shuffle the feature sets so we're not training on the same elements that we're testing on
'''
# write_out = open('featuresets.txt', 'w')
# write_out.writelines(str(featuresets))
# write_out.close()

random.shuffle(featuresets)

# positive data example:
training_set = featuresets[:10000]
testing_set =  featuresets[10000:]

### negative data example:
##training_set = featuresets[100:]
##testing_set =  featuresets[:100]

classifier_file = open('naivebayes.pickle', 'rb')
classifier = pickle.load(classifier_file)
classifier_file.close()

# classifier = nltk.NaiveBayesClassifier.train(training_set)
# print('Original Naive Bayes Algo accuracy percent:', (nltk.classify.accuracy(classifier, testing_set))*100)
# classifier.show_most_informative_features(15)

# save_classifier = open('naivebayes.pickle', 'wb')
# pickle.dump(classifier, save_classifier)
# save_classifier.close()

classifier_file = open('MNB.pickle', 'rb')
MNB_classifier = pickle.load(classifier_file)
classifier_file.close()
#
# MNB_classifier = SklearnClassifier(MultinomialNB())
# MNB_classifier.train(training_set)
# print('MNB Algo accuracy percent:', (nltk.classify.accuracy(MNB_classifier, testing_set))*100)

# save_classifier = open('MNB.pickle', 'wb')
# pickle.dump(MNB_classifier, save_classifier)
# save_classifier.close()
# print('pickled MNB_classifier')

classifier_file = open('BernoulliNBNB.pickle', 'rb')
BernoulliNBNB_classifier = pickle.load(classifier_file)
classifier_file.close()

# BernoulliNBNB_classifier = SklearnClassifier(BernoulliNB())
# BernoulliNBNB_classifier.train(training_set)
# print('BernoulliNB Algo accuracy percent:', (nltk.classify.accuracy(BernoulliNBNB_classifier, testing_set))*100)

# save_classifier = open('BernoulliNBNB.pickle', 'wb')
# pickle.dump(BernoulliNBNB_classifier, save_classifier)
# save_classifier.close()
# print('pickled BernoulliNBNB_classifier')

classifier_file = open('LogisticRegression.pickle', 'rb')
LogisticRegression_classifier = pickle.load(classifier_file)
classifier_file.close()

# LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
# LogisticRegression_classifier.train(training_set)
# print('LogisticRegression Algo accuracy percent:', (nltk.classify.accuracy(LogisticRegression_classifier, testing_set))*100)

# save_classifier = open('LogisticRegression.pickle', 'wb')
# pickle.dump(LogisticRegression_classifier, save_classifier)
# save_classifier.close()
# print('pickled LogisticRegression_classifier')

classifier_file = open('SGDClassifier.pickle', 'rb')
SGDClassifier_classifier = pickle.load(classifier_file)
classifier_file.close()

# SGDClassifier_classifier = SklearnClassifier(SGDClassifier())
# SGDClassifier_classifier.train(training_set)
# print('SGDClassifier Algo accuracy percent:', (nltk.classify.accuracy(SGDClassifier_classifier, testing_set))*100)

# save_classifier = open('SGDClassifier.pickle', 'wb')
# pickle.dump(SGDClassifier_classifier, save_classifier)
# save_classifier.close()
# print('pickled SGDClassifier_classifier')

# classifier_file = open('LinearSVC.pickle', 'rb')
# LinearSVC_classifier = pickle.load(classifier_file)
# classifier_file.close()

# LinearSVC_classifier = SklearnClassifier(LinearSVC())
# LinearSVC_classifier.train(training_set)
# print('LinearSVC Algo accuracy percent:', (nltk.classify.accuracy(LinearSVC_classifier, testing_set))*100)

# save_classifier = open('LinearSVC.pickle', 'wb')
# pickle.dump(LinearSVC_classifier, save_classifier)
# save_classifier.close()
# print('pickled LinearSVC_classifier')
#
classifier_file = open('NuSVC.pickle', 'rb')
NuSVC_classifier = pickle.load(classifier_file)
classifier_file.close()

# NuSVC_classifier = SklearnClassifier(NuSVC())
# NuSVC_classifier.train(training_set)
# print('NuSVC Algo accuracy percent:', (nltk.classify.accuracy(NuSVC_classifier, testing_set))*100)

# save_classifier = open('NuSVC.pickle', 'wb')
# pickle.dump(NuSVC_classifier, save_classifier)
# save_classifier.close()
# print('pickled NuSVC_classifier')

voted_classifier = VoteClassifier(classifier, MNB_classifier, BernoulliNBNB_classifier, LogisticRegression_classifier, SGDClassifier_classifier, NuSVC_classifier)
# voted_classifier = VoteClassifier(classifier)

# print('voted_classifier accuracy percent:', (nltk.classify.accuracy(voted_classifier, testing_set))*100)
#
# print('Classification:', voted_classifier.classify(testing_set[0][0]), 'Confidence %:', voted_classifier.confidence(testing_set[0][0])*100)
# print('Classification:', voted_classifier.classify(testing_set[1][0]), 'Confidence %:', voted_classifier.confidence(testing_set[1][0])*100)
# print('Classification:', voted_classifier.classify(testing_set[2][0]), 'Confidence %:', voted_classifier.confidence(testing_set[2][0])*100)
# print('Classification:', voted_classifier.classify(testing_set[3][0]), 'Confidence %:', voted_classifier.confidence(testing_set[3][0])*100)
# print('Classification:', voted_classifier.classify(testing_set[4][0]), 'Confidence %:', voted_classifier.confidence(testing_set[4][0])*100)
# print('Classification:', voted_classifier.classify(testing_set[5][0]), 'Confidence %:', voted_classifier.confidence(testing_set[5][0])*100)

def sentiment(text):
    feats = find_features(text)
    return voted_classifier.classify(feats),voted_classifier.confidence(feats)
