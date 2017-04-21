from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_googlemaps import GoogleMaps, Map, icons
from flask_bootstrap import Bootstrap
import tweepy, json, preprocess
import es_users, textblob
from textblob import TextBlob
import requests, pickle
import goldstandard_users
from jinja2 import Template
import pandas as pd
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection.univariate_selection import chi2, SelectKBest
import re
import pickle
import os.path
from wordcloud import WordCloud

model = pickle.load(open("models/symptoms/symptoms_SVM.pkl","rb"))
print "Model for syptoms loaded"

app = Flask(__name__)
Bootstrap(app)
ACCESS_TOKEN = ""
ACCESS_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
KEYWORDS = []
count_vec = TfidfVectorizer(analyzer="word", max_features=10000, ngram_range=(1,3), sublinear_tf=True)    
feat_select = SelectKBest(chi2, k=4000)
scaler = preprocessing.MinMaxScaler(feature_range=(0,1))

def tag_cloud(user, text):
	all_tweets = es_users.getStoredTweetsSize(user, 1000)
	text = ""
	for x in all_tweets:
		text = str(text) +  " " + str(x["_source"]["text"])
	wordcloud = WordCloud(scale = 1.5).generate(text)
	image = wordcloud.to_image()
	image.save("static/" + user + ".JPEG")
	return ("static/" + user + ".JPEG")
	
@app.route('/form')
def form():
   return render_template('form.html')



@app.route('/demo')
def demo():
	# All user's whose last status had a geo coordinate
    user_objects, place_user_objects, pigeo_objects = goldstandard_users.yes_users()
    user_objects.sort(key=lambda x: x['tweet_count'], reverse=True)
    pigeo_objects.sort(key=lambda x: x['tweet_count'], reverse=True)
    place_user_objects.sort(key=lambda x: x['tweet_count'], reverse=True)
    return render_template('demo.html', mark_json = user_objects, place_user_objects = place_user_objects, pigeo_objects = pigeo_objects)

@app.route('/sample')
def sample():
	# All user's whose last status had a geo coordinate
    user_objects, place_user_objects = es_users.getAllCoordinates()
    return render_template('new_home.html', mark_json = user_objects, place_user_objects = place_user_objects)

# @app.route('/')
# def student():
#     print "HI"
#     print "HI"
#     user_objects = es_users.getAllUserScreenNames()
#     markers = []
#     mark_json = []
#     for u_o in user_objects:
#     	for x in es_users.getStoredTweets(u_o["screen_name"]):
#     		x = json.dumps(x)
#     		x = json.loads(x)
#     		#print x 
#     		if x["_source"]["geo"] is not None:
#     			z = {}
#     			z["user_img"] = str(u_o["user_object"]["_source"]["profile_image_url"])
#     			#print z["user_img"]
#     			z["screen_name"] = str(u_o["screen_name"])
#     			z["lat"] = x["_source"]["geo"]["coordinates"][0]
#     			z["lng"] = x["_source"]["geo"]["coordinates"][1]
#     			markers.append(tuple(x["_source"]["geo"]["coordinates"]))
#     			mark_json.append(z)
#     			
#     		# if "coordinates" in x["_source"].keys():
# #     			print x["_source"]
# 		#u_o["user_object"]["_source"]["status"]["coordinates"]
#     markers = list(set(markers))
#     #print markers
#     m_list = [{'lat': 37.4419, 'lng': -122.1419}]
#     #print user_obj
#     #print len(markers)
#     #print markers[0]
#     #print mark_json[0]
#     print len(mark_json)
#     temp = {v['screen_name']:v for v in mark_json}.values()
#     mark_json = temp
#     print len(mark_json)
#     return render_template('sample.html', result = user_objects, m_list = markers, mark_json = mark_json)
      
def getAvgSentiment(user, all_tweets):
# 	all_tweets = es_users.getStoredTweets(user)
	print len(all_tweets)
	sum_senti = 0
	image_name = ""
	tweets = []
	print "Avg Senti"
	if len(all_tweets) > 1001:
		all_tweets = all_tweets[0:1000]
	for tweet in all_tweets:
		# processed_tweet = preprocess.preprocess_tweet(tweet["_source"]["text"])
# 		print processed_tweet
# 		pred = model.predict(processed_tweet)
# 		print pred[0]
# 		sys.exit()
		try:
			if tweet["_source"]["text"] not in tweets:
				tweets.append(tweet["_source"]["text"])
			blob = TextBlob(tweet["_source"]["text"])
			if blob.detect_language() is not "en":
				blob = blob.translate(to='en')
				tweet["_source"]["text"] = blob
		except:
			pass
    		#print blob
		for sentence in blob.sentences:
			sum_senti = sum_senti + sentence.sentiment.polarity
			print sum_senti
	avg_sent = (sum_senti/len(all_tweets))
	if os.path.exists("static/" + user + ".JPEG"):
		image_name = ("static/" + user + ".JPEG")
	else:
		print "IMG"
		image_name = tag_cloud(user, tweets)
	print avg_sent
	print image_name
	return avg_sent, image_name

@app.route('/<user>')
def user_profile(user):
    print "I'm running..."
    user_profile = es_users.getUser(user)
    if len(user_profile) == 0:
    	return render_template('form.html', error = 1)
    #if len(user_profile) > 0:
    tweets = es_users.getStoredTweetsSize(user, 10)
    print len(tweets)
    eng_tweets = []
    for tweet in tweets:
    	blob = TextBlob(tweet["_source"]["text"])
    	if blob.detect_language() is not "en":
    		#print blob
    		try:
    			blob = blob.translate(to='en')
    			tweet["_source"]["text"] = blob
    		except textblob.exceptions.NotTranslated:
    			pass
    		#print blob
    	eng_tweets.append(tweet)
    eng_tweets = eng_tweets[:10]
    avg_sent, image_name = getAvgSentiment(user, tweets)
    print avg_sent
    #print user
    #print user_profile
    #print user_profile[0]
    return render_template('user_profile.html', user = user_profile[0], tweets = eng_tweets, avg_sent = avg_sent, image_name = image_name)
    #return None

@app.route('/result',methods = ['POST', 'GET'])
def result():
   print "hi"
   if request.method == 'POST':
      result = request.form
      print result["SCREEN_NAME"] 
      result_link = result["SCREEN_NAME"]
      print result_link
      print url_for('user_profile', user=result_link)
      #return hello_name(result_link)
      return redirect(url_for('user_profile', user=result_link))
#       return render_template("user_profile", result = result)
    

if __name__ == '__main__':
    GoogleMaps(app, key = "AIzaSyDYRyuCbFOh_8ivTTnm1YjsXv4kKYWoPYc")
    app.run(debug = False, use_reloader = False)
    #app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))

 # import tweepy
 # import json
 #
 # # Authentication details. To  obtain these visit dev.twitter.com
 # consumer_key = 'nWGEdfoaBt7d6wWhiAw5Tw'
 # consumer_secret = 'qM4QfDPqG9JQp6n0fqTCMrj6LJjES6vu2IzqpZLc'
 # access_token = '2284416938-JbD4F32m9xQPMxKoh6UikpCLoJm8F6xy8wDPS9P'
 # access_token_secret = 'XvJZQWa6zz5vHcHkUcYBacQKZJE9pcxbpxUUgNo9rN4AG'
 #
 # # This is the listener, resposible for receiving data
 # class StdOutListener(tweepy.StreamListener):
 #     def on_data(self, data):
 #         # Twitter returns data in JSON format - we need to decode it first
 #         decoded = json.loads(data)
 #
 #         # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
 #         #print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
 #         print ''
 #         return True
 #
 #     def on_error(self, status):
 #         print status
 #
 # if __name__ == '__main__':
 #     l = StdOutListener()
 #     auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
 #     auth.set_access_token(access_token, access_token_secret)
 #
 #     print "Showing all new tweets for #programming:"
 #
 #     # There are different kinds of streams: public stream, user stream, multi-user streams
 #     # In this example follow #programming tag
 #     # For more details refer to https://dev.twitter.com/docs/streaming-apis
 #     stream = tweepy.Stream(auth, l)
 #     stream.filter(track=['programming'])
