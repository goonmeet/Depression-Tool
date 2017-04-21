from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV
import tweet_level_df
from sklearn.cross_validation import cross_val_score
import pandas as pd
import numpy as np
#from sklearn_pandas import DataFrameMapper, cross_val_score
#import sklearn.preprocessing, sklearn.decomposition,sklearn.linear_model, sklearn.pipeline, sklearn.metrics
#from sklearn.feature_extraction.text import CountVectorizer
from scipy import sparse
from nltk.corpus import sentiwordnet as swn
import matplotlib
from pylab import *
import tweet_level_df

############################################################-----------------------------------
#import os
import re
import logging
import pandas as pd
import numpy as np
import nltk.data
import sys
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from gensim.models import word2vec
from sklearn.preprocessing import Imputer
from sklearn import linear_model, naive_bayes, svm, preprocessing
#from sklearn import metrics
from sklearn.decomposition import TruncatedSVD
#from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.cross_validation import cross_val_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection.univariate_selection import chi2, SelectKBest
from sklearn.feature_selection import SelectKBest, chi2
#from sklearn.metrics import precision_score, recall_score, f1_score, cohen_kappa_score, make_scorer
import pickle
#import requests


# class Created_at_Extractor(BaseEstimator, TransformerMixin):
# 
#     def __init__(self, vars):
#         self.vars = vars  # e.g. pass in a column name to extract
# 
#     def transform(self, X, y=None):
#         return do_something_to(X['Created_at'], self.vars)  # where the actual feature extraction happens
# 
#     def fit(self, X, y=None):
#         return self  # generally does nothing
#         
# 
# 
# # build the feature matrices
# ngram_counter = CountVectorizer(ngram_range=(1, 4), analyzer='char')
# X_train = ngram_counter.fit_transform(tweet_level_df.get_goldstandard_df().Raw_text)
# # X_test  = ngram_counter.transform(data_test)
# 
# # train the classifier
# classifier = LinearSVC()
# model = classifier.fit(X_train, y_train)
# 
# # test the classifier
# # y_test = model.predict(X_test)
# 
# pipeline = Pipeline([
#     ('feats', FeatureUnion([
#         ('ngram', ngram_count_pipeline), # can pass in either a pipeline
#         ('created_at', Created_at_Extractor()) # or a transformer
#     ])),
#     ('clf', LinearSVC())  # classifier
# ])
# 
# # train the classifier
# # model = ppl.fit(data_train)
# 
# # test the classifier
# # y_test = model.predict(data_test)
# 
# scores = cross_validation.cross_val_score(classifier_pipeline, X_train.Raw_text, X_Annotation, cv=3)
# print scores
# # 
# # grid = GridSearchCV(pipeline, param_grid=pg, cv=5)
# # grid.fit(data_train, y_train)
# # 
# # grid.best_params_
# # # {'clf__C': 0.1}
# # 
# # grid.best_score_

if __name__ == "__main__":
	print "DONEEE"
	print "OOOSODFdf"
	svc = svm.LinearSVC(C=1.0)
	train_data = tweet_level_df.get_goldstandard_df()
	columns = ["Sentiment", "Created_at", "Month"]
	features = train_data[list(columns)].values
	print ("Training Support Vector Machine")
	cv_accuracy = cross_val_score(svc, features, train_data.Annotation, scoring="accuracy", cv=5)
	print ("CV Accuracy = %.4f" % cv_accuracy.mean())
	cv_prec = cross_val_score(svc, features, train_data.Annotation, scoring="precision_macro",  cv=5)
	print ("CV Precision = %.4f" % cv_prec.mean())
	cv_rec = cross_val_score(svc, features, train_data.Annotation, scoring="recall_macro", cv=5)
	print ("CV Recall = %.4f" % cv_rec.mean())
	cv_f1 = cross_val_score(svc, features, train_data.Annotation, scoring="f1_macro", cv=5)
	print ("CV F1 Score = %.4f" % cv_f1.mean())
	print ("Training Support Vector Machine")
	print ("CV Accuracy = %.4f" % cv_accuracy.mean())
	print ("CV Precision = %.4f" % cv_prec.mean())
	print ("CV Recall = %.4f" % cv_rec.mean())
	print ("CV F1 Score = %.4f" % cv_f1.mean())
        