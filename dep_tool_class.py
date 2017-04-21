'''
Created on Jul 22, 2016

@author: Lu Chen
'''
import pandas as pd
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection.univariate_selection import chi2, SelectKBest
import re
import pickle
import tweet_level_df
import logging
import pandas as pd
import numpy as np
import nltk.data
import sys
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
##################### Function Definition #####################

def clean_document(document, remove_stopwords=False, output_format="string"):
    """
    Input:
            document: raw text of a document
            remove_stopwords: a boolean variable to indicate whether to remove stop words
            output_format: if "string", return a cleaned string 
                            if "list", a list of words extracted from cleaned string.
    Output:
            Cleaned string or list.
    """
        
    # Remove HTML markup
    text = BeautifulSoup(document)
        
    # Keep only characters
    text = re.sub("[^a-zA-Z]", " ", text.get_text())
        
    # Split words and store to list
    text = text.lower().split()
        
    if remove_stopwords:
        
        # Use set as it has O(1) lookup time
        stops = set(stopwords.words("english"))
        words = [w for w in text if w not in stops]
        
    else:
        words = text
        
    # Return a cleaned string or list
    if output_format == "string":
        return " ".join(words)
            
    elif output_format == "list":
        return words

class Classifier:

    def __init__(self, train_data_file, model_file, num_dim = 4000):
        self.model_file = "models/symptoms/symptoms_SVM.pkl"
    
        #Initialization for sentiment classifier
        train_data = tweet_level_df.get_goldstandard_df()
        print len(train_data)
        sentiment_train_list = []
        train_data.Cleaned_text = train_data.Cleaned_text.fillna('')
        for i in range(0, len(train_data.Cleaned_text)):
        	text = ""
        	if pd.isnull(train_data.Cleaned_text[i]):
        		text = ""
        	else:
        		text = (train_data.Cleaned_text[i])
        	sentiment_train_list.append(train_data.Cleaned_text[i])
#         sentiment_train_list[np.isnan(sentiment_train_list)]= ""
#         np.place(sentiment_train_list, np.isnan(sentiment_train_list), "")
        print len(sentiment_train_list)
        self.count_vec = TfidfVectorizer(analyzer="word", max_features=10000, ngram_range=(1,3), sublinear_tf=True)      
        self.feat_select = SelectKBest(chi2, k=num_dim)
        train_vec = self.count_vec.fit_transform(sentiment_train_list)
        
#         sentiment_column = train_data[['Sentiment']].values
#         train_vec = sparse.hstack((train_vec, sentiment_column)).tocsr()
#         created_at_column = train_data[['Created_at']].values
#         train_vec = sparse.hstack((train_vec, created_at_column.astype(float))).tocsr()
#         month_column = train_data[['Month']].values
#         train_vec = sparse.hstack((train_vec, created_at_column.astype(float))).tocsr()

        train_vec = self.feat_select.fit_transform(train_vec, train_data.Annotation) 
        if "numpy.ndarray" not in str(type(train_vec)):
            train_vec = train_vec.toarray()
        self.scaler = preprocessing.MinMaxScaler(feature_range=(0,1))       
        train_vec = self.scaler.fit_transform(train_vec)
        # load the model
        self.model = pickle.load(open(model_file,"rb"))
    
    ##################### Classification Function #####################
    
    def classify(self, tweet):
        tweet_list = []
        tweet_list.append(str(clean_document(tweet)))
        print tweet_list
        # if the source is "user"
        tweet_vec = self.count_vec.transform(tweet_list)
        tweet_vec = self.feat_select.transform(tweet_vec)
        if "numpy.ndarray" not in str(type(tweet_vec)):
            tweet_vec = tweet_vec.toarray()  
        tweet_vec = self.scaler.transform(tweet_vec)
        print tweet_vec.shape
        pred = self.model.predict(tweet_vec)
       
        return pred[0]  
