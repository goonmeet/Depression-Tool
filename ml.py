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






##################### Initialization #####################

# term_vector_type = {"TFIDF", "Binary", "Int", "Word2vec", "Word2vec_pretrained"}
# {"TFIDF", "Int", "Binary"}: Bag-of-words model with {tf-idf, word counts, presence/absence} representation
# {"Word2vec", "Word2vec_pretrained"}: Google word2vec representation {without, with} pre-trained models
# Specify model_name if there's a pre-trained model to be loaded
vector_type = "TFIDF"
model_name = "GoogleNews-vectors-negative300.bin"

# model_type = {"bin", "reg"}
# Specify whether pre-trained word2vec model is binary
model_type = "bin"

# Parameters for word2vec
# num_features need to be identical with the pre-trained model
num_features = 300    # Word vector dimensionality
min_word_count = 40   # Minimum word count to be included for training
num_workers = 4       # Number of threads to run in parallel
context = 10          # Context window size
downsampling = 1e-3   # Downsample setting for frequent words

# training_model = {"RF", "NB", "LR", "SVM", "BT", "no"}
training_model = "SVM"

# feature scaling = {"standard", "signed", "unsigned", "no"}
# Note: Scaling is needed for SVM
scaling = "unsigned"

# dimension reduction = {"SVD", "chi2", "no"}
# Note: For NB models, we cannot perform truncated SVD as it will make input negative
# chi2 is the feature selectioin based on chi2 independence test
dim_reduce = "no"
num_dim = 3000

# campaign, and target entity
campaign_name = "symptoms"
target_name = "symptoms"
# train data file
# train_data_file = "../data/" + campaign_name + "/" + target_name + ".csv"
# model file
save_model = True
model_file = "models/" + campaign_name + "/" + target_name + "_" + training_model + ".pkl"
preprocess = False
##################### End of Initialization #####################



##################### Function Definition #####################

def clean_document(document, remove_stopwords = False, output_format = "string"):
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

def document_to_doublelist(document, tokenizer, remove_stopwords = False):
    """
    Function which generates a list of lists of words from a document for word2vec uses.

    Input:
        document: raw text of a document
        tokenizer: tokenizer for sentence parsing
                   nltk.data.load('tokenizers/punkt/english.pickle')
        remove_stopwords: a boolean variable to indicate whether to remove stop words

    Output:
        A list of lists.
        The outer list consists of all sentences in a document.
        The inner list consists of all words in a sentence.
    """

    # Create a list of sentences
    raw_sentences = tokenizer.tokenize(document.strip())
    sentence_list = []

    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentence_list.append(clean_document(raw_sentence, False, "list"))
    return sentence_list

def document_to_vec(words, model, num_features):
    """
    Function which generates a feature vector for the given document.

    Input:
        words: a list of words extracted from a document
        model: trained word2vec model
        num_features: dimension of word2vec vectors

    Output:
        a numpy array representing the document
    """

    feature_vec = np.zeros((num_features), dtype="float32")
    word_count = 0

    # index2word is a list consisting of all words in the vocabulary
    # Convert list to set for speed
    index2word_set = set(model.index2word)

    for word in words:
        if word in index2word_set:
            word_count += 1
            feature_vec += model[word]

    feature_vec /= word_count
    return feature_vec

def gen_document_vecs(documents, model, num_features):
    """
    Function which generates a m-by-n numpy array from all documents,
    where m is len(documents), and n is num_feature

    Input:
            documents: a list of lists.
                     Inner lists are words from each content.
                     Outer lists consist of all documents
            model: trained word2vec model
            num_feature: dimension of word2vec vectors
    Output: m-by-n numpy array, where m is len(content) and n is num_feature
    """

    curr_index = 0
    doc_feature_vecs = np.zeros((len(documents), num_features), dtype="float32")

    for review in documents:
        if curr_index%1000 == 0.:
            print ("Vectorizing content %d of %d", curr_index, len(documents))
        doc_feature_vecs[curr_index] = document_to_vec(review, model, num_features)
        curr_index += 1

    return doc_feature_vecs

##################### End of Function Definition #####################


########################### Main Program ###########################
print ("test")

train_list = []
word2vec_input = []
pred = []

#train_data = pd.read_csv(train_data_file, hsignedeader=0, delimiter="\t", encoding="utf-8", quoting=3)
#train_data = pd.read_csv(train_data_file, delimiter="\t", encoding="utf-8", quoting=3)
train_data = tweet_level_df.get_goldstandard_df()
train_data = train_data.dropna()
print train_data.loc[60]
# print (pd.isnull(train_data))
print train_data.columns
print train_data.Raw_text.loc[0]

#print (train_data.tail(2000))
#sys.exit()
# train_data.columns = ['id', 'sentiment', 'content','textBlob','pos_counts','neg_counts','negative_hashtag_count','positive_hashtag_count']
#print(train_data.postive_hashtag_count)
#sys.exit()
#print ("heeeeeeeeeeeeereeee")
#sys.exit()


if vector_type == "Word2vec":
    unlab_train_data = pd.read_csv("unlabeledTrainData.tsv", header=0, delimiter="\t", quoting=3)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)


# Extract words from documents
# range is faster when iterating
if vector_type == "Word2vec" or vector_type == "Word2vec_pretrained":

    for i in range(0, len(train_data.content)):
        if vector_type == "Word2vec":
            # Decode utf-8 coding first
            word2vec_input.extend(document_to_doublelist(train_data.content[i].decode("utf-8"), tokenizer))

        train_list.append(clean_document(train_data.content[i], output_format="list"))
        if i%1000 == 0:
            print ("Cleaning training content", i)

    if vector_type == "Word2vec":
        for i in range(0, len(unlab_train_data.content)):
            word2vec_input.extend(document_to_doublelist(unlab_train_data.content[i].decode("utf-8"), tokenizer))
            if i%1000 == 0:
                print ("Cleaning unlabeled training content", i)

elif vector_type != "no":
	
	if preprocess == True:
		for i in range(0, len(train_data.content)):
		        	# Append raw texts rather than lists as Count/TFIDF vectorizers take raw texts as inputs

			try:
				train_list.append(clean_document(train_data.content[i]))
            	#print ("trainlist--->",train_list[i])

			except Exception as e:
				raise


# Generate vectors from words
if vector_type == "Word2vec_pretrained" or vector_type == "Word2vec":

    if vector_type == "Word2vec_pretrained":
        print ("Loading the pre-trained model")
        if model_type == "bin":
            model = word2vec.Word2Vec.load_word2vec_format(model_name, binary=True)
        else:
            model = word2vec.Word2Vec.load(model_name)

    if vector_type == "Word2vec":
        print ("Training word2vec word vectors")
        model = word2vec.Word2Vec(word2vec_input, workers=num_workers, \
                                size=num_features, min_count = min_word_count, \
                                window = context, sample = downsampling)

        # If no further training and only query is needed, this trims unnecessary memory
        model.init_sims(replace=True)

        # Save the model for later use
        model.save(model_name)

    print ("Vectorizing training contennp.asarray(vectorizer.get_feature_names())[ch2.get_support()]t")
    train_vec = gen_document_vecs(train_list, model, num_features)

elif vector_type != "no":
    if vector_type == "TFIDF":
        # Unit of gshow()ram is "word", only top 5000/10000 words are extracted
        count_vec = TfidfVectorizer(analyzer="word", max_features=1, ngram_range=(1,3), sublinear_tf=True)

    elif vector_type == "Binary" or vector_type == "Int":
        count_vec = CountVectorizer(analyzer="word", max_features=10000, \
                                    binary = (vector_type == "Binary"), \
                                    ngram_range=(1,3))

    # Return a scipy sparse term-document matrix
    print ("Vectorizing input texts")



    train_vec = count_vec.fit_transform(train_data.Cleaned_text)
    
#     sentiment_column = train_data[['Sentiment']].values
#     train_vec = sparse.hstack((train_vec, sentiment_column)).tocsr()
#     
#     created_at_column = train_data[['Created_at']].values
#     train_vec = sparse.hstack((train_vec, created_at_column.astype(float))).tocsr()
#     
#     month_column = train_data[['Month']].values
#     train_vec = sparse.hstack((train_vec, created_at_column.astype(float))).tocsr()
    
    print "Here"

    # new_text_blob = train_data[['textBlob']].values
    # train_vec = sparse.hstack((train_vec, new_text_blob)).tocsr()
    #
#     pos_counts = train_data[['pos_counts']].values
#     train_vec = sparse.hstack((train_vec, pos_counts)).tocsr()
# 
#     neg_counts = train_data[['neg_counts']].values
#     train_vec = sparse.hstack((train_vec, neg_counts)).tocsr()


    # pos_counts_hashtags = train_data[['positive_hashtag_count']].values
    # train_vec = sparse.hstack((train_vec, pos_counts_hashtags)).tocsr()
    #
    # neg_counts_hashtags = train_data[['negative_hashtag_count']].values
    # train_vec = sparse.hstack((train_vec, neg_counts_hashtags)).tocsr()

    print ("train_vec.shape",train_vec.shape)
    #print (train_vec)
#     sys.exit()

####################### HEREEEEE ################################################


if scaling != "no":
    #max_abs_scaler = preprocessing.MaxAbsScaler(max_abs_scaler = preprocessing.MaxAbsScaler())
    if scaling == "standard":
        scaler = preprocessing.StandardScaler(with_mean=False)
    else:
        if scaling == "unsigned":
            #scaler = preprocessing.MinMaxScaler(feature_range=(0,1))
            scaler = preprocessing.MaxAbsScaler()

        elif scaling == "signed":
            scaler = preprocessing.MinMaxScaler(feature_range=(-1,1))

    print ("Scaling vectors")
    train_vec = scaler.fit_transform(train_vec)
#     print (train_vec)

    #sys.exit()

# Feature Scaling
# Dimemsion Reduction
if dim_reduce == "SVD":
    print ("Performing dimension reduction")
    svd = TruncatedSVD(n_components = num_dim)
    train_vec = svd.fit_transform(train_vec)
    print ("Explained variance ratio =", svd.explained_variance_ratio_.sum())

elif dim_reduce == "chi2":
    print ("Performing feature selection based on chi2 independence test")
    chi2score = chi2(train_vec,train_data.sentiment)[0]
    ##################
    fselect = SelectKBest(chi2, k = num_dim)
    train_vec = fselect.fit_transform(train_vec, train_data.sentiment)
    #print (train_vec.get_feature_names())


    figure(figsize=(6,6))
    wscores = zip(count_vec.get_feature_names(),chi2score)
    wchi2 = sorted(wscores,key=lambda x:x[1])
    topchi2 = list(zip(*wchi2[-100:]))
    x = range(len(topchi2[1]))
    #print(len(topchi2[1]))
    #sys.exit()
    labels = topchi2[0]
    barh(x,topchi2[1],align='center',alpha=.2,color='g')
    plot(topchi2[1],x,'-o',markersize=2,alpha=.8,color='g')
    yticks(x,labels)
    xlabel('$\chi^2$')
    #show()


    # new_text_blob = train_data[['textBlob']].values
    # train_vec = sparse.hstack((train_vec, new_text_blob)).tocsr()
    #
    # pos_counts = train_data[['pos_counts']].values
    # train_vec = sparse.hstack((train_vec, pos_counts)).tocsr()
    #
    # neg_counts = train_data[['neg_counts']].values
    # train_vec = sparse.hstack((train_vec, neg_counts)).tocsr()


    pos_counts_hashtags = train_data[['positive_hashtag_count']].values
    train_vec = sparse.hstack((train_vec, pos_counts_hashtags)).tocsr()

    neg_counts_hashtags = train_data[['negative_hashtag_count']].values
    train_vec = sparse.hstack((train_vec, neg_counts_hashtags)).tocsr()

    print ("train_vec.shape",train_vec.shape)
    #sys.exit()


# Transform into numpy arrays
if "numpy.ndarray" not in str(type(train_vec)):
    train_vec = train_vec.toarray()



# Model training
if training_model == "RF" or training_model == "BT":
    # Initialize the Random Forest or bagged tree based the model chosen
    rfc = RFC(n_estimators = 100, oob_score = True, \
              max_features = (None if training_model=="BT" else "auto"))
    cv_accuracy = cross_val_score(rfc, train_vec, train_data.sentiment, scoring="accuracy", cv=5)
    cv_prec = cross_val_score(rfc, train_vec, train_data.sentiment, scoring="precision_macro",  cv=5)
    cv_rec = cross_val_score(rfc, train_vec, train_data.sentiment, scoring="recall_macro", cv=5)
    cv_f1 = cross_val_score(rfc, train_vec, train_data.sentiment, scoring="f1_macro", cv=5)
    print ("Training %s" % ("Random Forest" if training_model=="RF" else "bagged tree"))
    print ("CV Accuracy = %.4f" % cv_accuracy.mean())
    print ("CV Precision = %.4f" % cv_prec.mean())
    print ("CV Recall = %.4f" % cv_rec.mean())
    print ("CV F1 Score = %.4f" % cv_f1.mean())
    rfc = rfc.fit(train_vec, train_data.sentiment)
    print ("OOB Score =", rfc.oob_score_)
    if save_model:
        f = open(model_file, "wb")
        pickle.dump(rfc, f)

elif training_model == "NB":
    nb = naive_bayes.MultinomialNB()
    cv_accuracy = cross_val_score(nb, train_vec, train_data.sentiment, scoring="accuracy", cv=5)
    cv_prec = cross_val_score(nb, train_vec, train_data.sentiment, scoring="precision_macro",  cv=5)
    cv_rec = cross_val_score(nb, train_vec, train_data.sentiment, scoring="recall_macro", cv=5)
    cv_f1 = cross_val_score(nb, train_vec, train_data.sentiment, scoring="f1_macro", cv=5)
    print ("Training Naive Bayes")
    print ("CV Accuracy = %.4f" % cv_accuracy.mean())
    print ("CV Precision = %.4f" % cv_prec.mean())
    print ("CV Recall = %.4f" % cv_rec.mean())
    print ("CV F1 Score = %.4f" % cv_f1.mean())
    nb = nb.fit(train_vec, train_data.sentiment)
#    f = open("../models/edrugtrend_nb_model_sentiment.pkl","wb")
    if save_model:
        f = open(model_file, "wb")
        pickle.dump(nb, f)

elif training_model == "LR":
    lr = linear_model.LogisticRegression(dual=False, \
                class_weight="balanced", solver='lbfgs', multi_class="multinomial")
    cv_accuracy = cross_val_score(lr, train_vec, train_data.sentiment, scoring="accuracy", cv=5)
    cv_prec = cross_val_score(lr, train_vec, train_data.sentiment, scoring="precision_macro",  cv=5)
    cv_rec = cross_val_score(lr, train_vec, train_data.sentiment, scoring="recall_macro", cv=5)
    cv_f1 = cross_val_score(lr, train_vec, train_data.sentiment, scoring="f1_macro", cv=5)
    print ("Training Logistic Regression")
    print ("CV Accuracy = %.4f" % cv_accuracy.mean())
    print ("CV Precision = %.4f" % cv_prec.mean())
    print ("CV Recall = %.4f" % cv_rec.mean())
    print ("CV F1 Score = %.4f" % cv_f1.mean())
    lr = lr.fit(train_vec, train_data.sentiment)
    if save_model:
        f = open(model_file, "wb")
        pickle.dump(lr, f)

elif training_model == "SVM":
    svc = svm.LinearSVC(C=1.0)
#    svc = svm.SVC(C=1.0)
#    param = {'C': [1e15,1e13,1e11,1e9,1e7,1e5,1e3,1e1,1e-1,1e-3,1e-5]}
    print ("Training SVM")
#    f1_macro = metrics.make_scorer(metrics.f1_score, pos_label=None, average='macro')
#    svc = GridSearchCV(svc, param, score_func = metrics.accuracy_score, cv=5)
	
    cv_accuracy = cross_val_score(svc, train_vec, train_data.Annotation, scoring="accuracy", cv=5)
    cv_prec = cross_val_score(svc, train_vec, train_data.Annotation, scoring="precision_macro",  cv=5)
    cv_rec = cross_val_score(svc, train_vec, train_data.Annotation, scoring="recall_macro", cv=5)
    cv_f1 = cross_val_score(svc, train_vec, train_data.Annotation, scoring="f1_macro", cv=5)
    print ("Training Support Vector Machine")
    print ("CV Accuracy = %.4f" % cv_accuracy.mean())
    print ("CV Precision = %.4f" % cv_prec.mean())
    print ("CV Recall = %.4f" % cv_rec.mean())
    print ("CV F1 Score = %.4f" % cv_f1.mean())
    show()
    svc = svc.fit(train_vec, train_data.Annotation)
#    print ("Optimized parameters:", svc.best_estimator_)
#    print ("Best CV score:", svc.best_score_)
    if save_model:
        f = open(model_file, "wb")
        pickle.dump(svc, f)



