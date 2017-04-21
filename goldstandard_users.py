import requests, pigeo, ast
import json, es_users, sys, os
import csv
import yaml
from TwitterAPI import *
from twitter import *
from twitter import Twitter
from time import sleep, time
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import urllib, cStringIO
import Image
import pytesseract
from geotext import GeoText
geo_users = []
profile_loc_users = []
piego_users = []
from nltk import word_tokenize, pos_tag
from nltk.tokenize import TweetTokenizer
tknzr = TweetTokenizer()
from collections import Counter
# pos_tag(word_tokenize(text))
import sys
from pandas.io.json import json_normalize 
from wordcloud import WordCloud
reload(sys)
sys.setdefaultencoding('utf8')
from nltk.corpus import stopwords
stop = set(stopwords.words('english'))
cusswords = data = [line.strip() for line in open("profane_common.txt", 'r')]

def getHashtags(screen_name):
	user_tweet_objs = es_users.getStoredTweets(screen_name)
	hashtags = []
	for tweet in user_tweet_objs:
		tweet_words = tknzr.tokenize(tweet["_source"]["text"])
		for x in tweet_words:
			if "#" in x:
				hashtags.append(str(x))
# 	print Counter(hashtags)
# 	print dict(Counter(hashtags))
# 	sys.exit()
	return 	dict(Counter(hashtags))

def parse_location(user_profile_json, tag, u_o):
	#print user_profile_json[tag]
	pigeo_used = False
	tagged = pos_tag(word_tokenize(str(user_profile_json[tag])))
# 	pharse = False
# 	for x in tagged:
# 		if "NNP" not in x:
# 			pharse = True
# 	if pharse:
# 		print user_profile_json[tag]
	places = GeoText(str(user_profile_json[tag]))
	if len(places.cities) == 0:
		if len(places.countries) == 0:
			u_o["lat"], u_o["lng"] = es_users.pigeo_result(u_o["screen_name"])
			piego_users.append(u_o)
		else:
			print user_profile_json[tag]
			pharse = False
			for x in tagged:
				if "NNP" not in x:
					pharse = True
			if pharse:
				print user_profile_json[tag]
			determine_location(user_profile_json[tag],u_o["screen_name"], u_o)
	else:
		print user_profile_json[tag]
		pharse = False
		for x in tagged:
			if "NNP" not in x:
				pharse = True
		if pharse:
			print user_profile_json[tag]
		determine_location(user_profile_json[tag],u_o["screen_name"], u_o)

def determine_location(text, screen_name, u_o):
	#print text
	response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyDYRyuCbFOh_8ivTTnm1YjsXv4kKYWoPYc&address=' + str(text))
	resp_json_payload = response.json()
	pigeo_used = False
	if len(resp_json_payload['results']) > 0:
		u_o["lat"] = resp_json_payload['results'][0]['geometry']['location']["lat"]
		u_o["lng"] = resp_json_payload['results'][0]['geometry']['location']["lng"]
		profile_loc_users.append(u_o)
	else:
		u_o["lat"], u_o["lng"] = es_users.pigeo_result(screen_name)
		piego_users.append(u_o)
	#print u_o

def get_all_user_names_test():
	users = es_users.getAllUsers()
	user_names = []
	for user in users:
		user_names.append(user["_id"])
	df = pd.DataFrame({'USER_ID': user_names})
	return df

def parse_user_tweet_obj(user_profile_json):
	u_o = {}
# 	user_profile_json = json.dumps(json.loads(user_profile_json))
	u_o["screen_name"] = str(user_profile_json["screen_name"])
# 	print u_o["screen_name"]
	u_o["user_img"] = str(user_profile_json["profile_image_url_https"]).replace("_normal", "")
	u_o["tweet_count"] = es_users.getStoredTweetCount(u_o["screen_name"])
	if ("status" in user_profile_json):
		if (user_profile_json["status"]["geo"] is not None):
			u_o["lat"] = user_profile_json["status"]["geo"]["coordinates"][0]
			u_o["lng"] = user_profile_json["status"]["geo"]["coordinates"][1]
			geo_users.append(u_o)
			print u_o
			return 0
	if ("profile_location" in user_profile_json) and (user_profile_json["profile_location"] is not None):
		parse_location(user_profile_json, "profile_location", u_o)
		return 0
	elif ("location" in user_profile_json) and (user_profile_json["location"] is not None):
		parse_location(user_profile_json, "location", u_o)
		return 0
	else:
		u_o["lat"], u_o["lng"] = es_users.pigeo_result(u_o["screen_name"])
		piego_users.append(u_o)
		return 0
	
			
	
	sys.exit()
	
# 	users_with_status_coordinates.append(str(x["_id"]))
# 	u_o["user_img"] = str(x["_source"]["profile_image_url_https"]).replace("_normal", "")
# 	u_o["lat"] = x["_source"]["status"]["geo"]["coordinates"][0]
# 	u_o["lng"] = x["_source"]["status"]["geo"]["coordinates"][1]
# 	u_o["tweet_count"] = getStoredTweetCount(u_o["screen_name"])
# 	user_objs.append(u_o)
# 	if "coordinates" in tweet_obj:
# 		geo_users.append(tweet_obj)
# 		sys.exit()
# 	elif "place" in tweet_obj:
# 		profile_loc_users.append(tweet_obj)
# 	else:
# 		piego_users.append(tweet_obj)
# 	u_o = {} 



def get_user_tweet_objs(screen_name):
	tweet_jsons = es_users.getStoredTweets(screen_name)
	if len(tweet_jsons) == 0:
		return None
	all_user_tweet_obj = []
	tweet_obj = {}
	#print screen_name
	for tweet_json in tweet_jsons:
		img_text = ""
		img_url = ""
		#print tweet_json["_source"]
		tweet_json = json.loads(json.dumps(tweet_json))
		tweet_obj["es_id"] = tweet_json["_id"]
		tweet_obj["text"] = tweet_json["_source"]["text"]
		#print tweet_obj["text"]
		tweet_obj["created_at"] = tweet_json["_source"]["created_at"]
		tweet_obj["favorite_count"] = tweet_json["_source"]["favorite_count"]
		tweet_obj["retweet_count"] = tweet_json["_source"]["retweet_count"]
		tweet_obj["twitter_id_str"] = tweet_json["_source"]["id_str"]
		tweet_obj["lang"] = tweet_json["_source"]["lang"]
		if "place" in tweet_json["_source"]:
			if ["place"] is not None:
				tweet_obj["place"] = tweet_json["_source"]["place"]
		if "coordinates" in tweet_json:
			if "coordinates" in tweet_json["coordinates"]:
				tweet_obj["coordinates"] = tweet_json["geo"]["coordinates"]["coordinates"]
		if "entities" in tweet_json["_source"]:
			if ("media" in tweet_json["_source"]["entities"]) and (tweet_json["_source"]["entities"]["media"] is not None):
				img_text = ""
				for x in tweet_json["_source"]["entities"]["media"]:
					img_url = str(x["media_url_https"])
					file = cStringIO.StringIO(urllib.urlopen(str(x["media_url_https"])).read())
					img = Image.open(file)
					img_text = pytesseract.image_to_string(img)
					print img_text
		tweet_obj["img_text"] = str(img_text)
		tweet_obj["img_url"] = img_url
		
		#print tweet_obj
		#all_user_tweet_obj.append(tweet_obj)
		tweet_obj = {}
	#print len(all_user_tweet_obj)
	#Get all unique tweets:
# 	unique_tweets = []
# 	unique_tweets_obj = []
	# for x in all_user_tweet_obj:
# 		#print x
# 		if x["text"] not in unique_tweets:
# 			unique_tweets_obj.append(x)
# 			unique_tweets.append(x["text"])
# 			#print len(unique_tweets_obj)
# 	all_user_tweet_obj = unique_tweets_obj
	#print len(all_user_tweet_obj)
	#syst.exit()
	return all_user_tweet_obj

def get_user_data(list_df):
    df_rows = []
    for index, row in list_df.iterrows():
	    user_profile_json = es_users.getUserProfile(row['USER_ID'])
	    if (user_profile_json == []):
	        x = 1
	    else:
	        user_profile_json = user_profile_json[0]
	        user_profile_json = json.loads(json.dumps(user_profile_json["_source"]))
	        user_tweets_obj = get_user_tweet_objs(row['USER_ID'])
	        if user_tweets_obj is None:
				continue
	        user_all_tweets_string, avg_fav_count, avg_retweet_count, min_fav_count, max_fav_count = user_tweets_string(user_tweets_obj)# avg_fav_count, avg_retweet_count, min_fav_count, max_fav_count = 0
	        if user_all_tweets_string is None:
				continue
	        user_profile_json["tweets"] = user_all_tweets_string
	        user_profile_json["avg_fav_count"] = avg_fav_count
	        user_profile_json["avg_retweet_count"] = avg_retweet_count
	        user_profile_json["min_fav_count"] = min_fav_count
	        user_profile_json["max_fav_count"] = max_fav_count
	        df_rows.append(user_profile_json)
    user_data = json_normalize(df_rows)
    #print list(user_data)
    #print len(list(user_data))
    #print user_data
    return user_data

def user_tweets_string(user_tweets_obj):
	user_all_tweets_string = ""
	sum_fav_count = 0
	max_fav_count = 0
	min_fav_count = 0
	sum_retweet_count = 0
	for user_tweet_obj in user_tweets_obj:
		#print user_tweet_obj["text"]
		user_all_tweets_string = user_all_tweets_string + (user_tweet_obj["text"] .replace("\n", " "))
		sum_retweet_count = user_tweet_obj["retweet_count"] + sum_retweet_count
		sum_fav_count = user_tweet_obj["favorite_count"] + sum_fav_count
		if user_tweet_obj["favorite_count"] > max_fav_count:
			max_fav_count = user_tweet_obj["favorite_count"]
		if user_tweet_obj["favorite_count"] < min_fav_count:
			min_fav_count = user_tweet_obj["favorite_count"]
	avg_fav_count = sum_fav_count / (len(user_tweets_obj)*1.0)
	avg_retweet_count = sum_retweet_count / (len(user_tweets_obj)*1.0)
	# print user_all_tweets_string
	# print "avg fav " + str(avg_fav_count)
	# print "avg retweet " + str(avg_retweet_count)
	# print "max fav " + str(max_fav_count)
	# print "min fav " + str(min_fav_count)
	return user_all_tweets_string, avg_fav_count, avg_retweet_count, min_fav_count, max_fav_count

def get_yes_users():
	print "Making yes"
	user_type = "yes"
	df_ric = pd.read_csv("profile_goldstandard_ric.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	df_des = pd.read_csv("profile_goldstandard_des.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	df_meet = pd.read_csv("profile_goldstandard_meet.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	foo = "DEPRESSED/NO"
# 	serverNumber = sys.argv[1]
	yes_df =  df_ric.loc[df_ric["DEPRESSED/NO"] == user_type]
	print len(yes_df)
	yes_df_des = (df_des.loc[df_des["DEPRESSED/NO"] == user_type])
	yes_df = yes_df.append(yes_df_des)
	print len(yes_df)
	yes_df = yes_df.append(df_meet)
	print len(yes_df)
	print df_meet.loc[0]['USER_ID']
	depressed_users = []
	geo_file = open('geo_users.csv', 'a')
	for index, row in yes_df.iterrows():
		user_profile_json = es_users.getUserProfile(row['USER_ID'])
		if len(user_profile_json) == 0:
			x = 1
# 			print row['USER_ID']
		else:
			user_profile_json = user_profile_json[0]
			user_profile_json = user_profile_json["_source"]
			depressed_users.append(row['USER_ID'])
			parse_user_tweet_obj(user_profile_json)
		#print geo_users
		#print profile_loc_users
		#print piego_users
# 		geo_file = open('geo_users.csv', 'a')
		if len(geo_users):
			result = json_normalize(geo_users)
			result.to_csv("geo_users.csv", sep=',', quoting=csv.QUOTE_ALL, quotechar='"')
		if len(profile_loc_users):
			result = json_normalize(profile_loc_users)
			result.to_csv("profile_loc_users.csv", sep=',', quoting=csv.QUOTE_ALL, quotechar='"')
		if len(piego_users):
			result = json_normalize(piego_users)
			result.to_csv("piego_users.csv", sep=',', quoting=csv.QUOTE_ALL, quotechar='"')
	print len(depressed_users)

def yes_users():

	geo_users = pd.read_csv('geo_users.csv')
	geo_users = geo_users.drop(geo_users.columns[[0]], axis=1)
	geo_users = geo_users.to_json(orient='records')
	geo_users = json.dumps(json.loads(geo_users))
	geo_users = yaml.safe_load(geo_users)
	
	
	profile_loc_users = pd.read_csv('profile_loc_users.csv')
	profile_loc_users = profile_loc_users.drop(profile_loc_users.columns[[0]], axis=1)
	profile_loc_users = profile_loc_users.to_json(orient='records')	
	profile_loc_users = json.dumps(json.loads(profile_loc_users))
	profile_loc_users = yaml.safe_load(profile_loc_users)

	piego_users = pd.read_csv('piego_users.csv')
	piego_users = piego_users.drop(piego_users.columns[[0]], axis=1)
	piego_users = piego_users.to_json(orient='records')	
	piego_users = json.dumps(json.loads(piego_users))
	piego_users = yaml.safe_load(piego_users)

	return geo_users, profile_loc_users, piego_users
	
def top_words_in_tweets(screen_name):
	cusswords_count = 0
	user_tweet_objs = es_users.getStoredTweets(screen_name)
	words = []
	for tweet in user_tweet_objs:
		tweet_words = tknzr.tokenize(tweet["_source"]["text"])
		for x in tweet_words:
			if str(x).lower() not in stop:
				words.append(str(x).lower())
			if str(x).lower() in cusswords:
				cusswords_count = cusswords_count + 1
# 	print Counter(hashtags)
# 	sys.exit()
	return words, cusswords_count

def top_words_in_description(user_profile_json):
	words = []
# 	print user_profile_json[0]["_source"]["description"]
	tweet_words = tknzr.tokenize(user_profile_json[0]["_source"]["description"])
	for x in tweet_words:
		if str(x).lower() not in stop:
			words.append(str(x).lower())
# 	print Counter(hashtags)
# 	print dict(Counter(words))
# 	sys.exit()
	return	dict(Counter(words))	
				
def count(user_type):
# 	test_data = get_user_data(get_all_user_names_test())
# 	print "Done with test data frame"
	df_ric = pd.read_csv("profile_goldstandard_ric.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	df_des = pd.read_csv("profile_goldstandard_des.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	df_meet = pd.read_csv("profile_goldstandard_meet.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	foo = "DEPRESSED/NO"
# 	serverNumber = sys.argv[1]
	yes_df =  df_ric.loc[df_ric["DEPRESSED/NO"] == user_type]
	yes_df = yes_df.reset_index()
	print len(yes_df)
	yes_df_des = (df_des.loc[df_des["DEPRESSED/NO"] == user_type])
	yes_df = yes_df.append(yes_df_des, ignore_index = True)
	print len(yes_df)
	yes_df = yes_df.append(df_meet, ignore_index = True)
	print len(yes_df)
	for index, row in yes_df.iterrows():
		print index

def main(user_type):
	print user_type
# 	test_data = get_user_data(get_all_user_names_test())
# 	print "Done with test data frame"
	df_ric = pd.read_csv("profile_goldstandard_ric.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	df_des = pd.read_csv("profile_goldstandard_des.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	df_meet = pd.read_csv("profile_goldstandard_meet.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c')
	foo = "DEPRESSED/NO"
# 	serverNumber = sys.argv[1]
	yes_df =  df_ric.loc[df_ric["DEPRESSED/NO"] == user_type]
	yes_df = yes_df.reset_index()
	print len(yes_df)
	yes_df_des = (df_des.loc[df_des["DEPRESSED/NO"] == user_type])
	yes_df = yes_df.append(yes_df_des, ignore_index = True)
	print len(yes_df)
	user_type_list = []
	if user_type == "yes":
		yes_df = yes_df.append(df_meet, ignore_index = True)
		print df_meet.loc[0]['USER_ID']
	print len(yes_df)
	#no_df =  df.loc[df['DEPRESSED/NO'] == "no"]
	all_words = []
	top_discript = {}
	all_hashtags = {}
	total_cusswords_count = 0
	for index, row in yes_df.iterrows():
		user_profile_json = es_users.getUserProfile(row['USER_ID'])
		fo = open(user_type + "_users.txt", 'r')
		user_type_list = [line.strip() for line in fo] 
# 		print user_profile_json
		if len(user_profile_json) == 0:
			print row['USER_ID']
			continue
		elif str(row['USER_ID']) in user_type_list:
			print row['USER_ID']
			print "Already done"
			continue
		else:
# 			print all_words
# 			sys.exit()
			print row['USER_ID']
			fo.close()
			user_type_list.append(row['USER_ID'])
			user_type_list_thefile = open(user_type + "_users.txt", 'w')
			user_type_list_thefile.write(str('\n'.join(user_type_list)))
			words, cusswords_count = top_words_in_tweets(row['USER_ID'])
			total_cusswords_count = total_cusswords_count + cusswords_count
			all_words = all_words + words
			top_discript.update(top_words_in_description(user_profile_json))
			hashtags = getHashtags(row['USER_ID'])
			all_hashtags.update(hashtags)
			json.dump(all_hashtags, open(user_type + "_top_hashtags.txt",'w'))
			thefile = open("all_words_" + user_type + ".txt", 'w')
			for item in all_words:
				thefile.write("%s\n" % item)
			json.dump(top_discript, open(user_type + "_top_words_disc.txt",'w'))
		print index
		print "{} number of cusswords in {}".format(total_cusswords_count, user_type)
		total_cusswords_count_file = open("total_cusswords_count_" + user_type + ".txt", 'w')
		total_cusswords_count_file.write(str(total_cusswords_count))
	# yes_user_data = get_user_data(yes_df)
# 	print "Done with yes data frame"
# 	no_user_data = get_user_data(no_df)
# 	print "Done with no data frame"
    #print (list(yes_user_data))
    #print yes_user_data.ix[0]["tweets"]
    #print no_user_data.ix[0]
    #print len(get_user_tweet_objs("rahzamdy"))


# def get_user_data(yes_df):
#     df_rows = []
#     df_cols = []
#
#     row_index = -1
#     #print list(yes_df)
#     for index, row in yes_df.iterrows():
#         user_profile_json = es_users.getUserProfile(row['USER_ID'])
#         if user_profile_json == []:
#             x = 1
#             #print row['USER_ID']
#         else:
#             row_index = row_index + 1
#             user_profile_json = user_profile_json[0]
#             #print user_profile_json
#             user_profile_json = json.loads(json.dumps(user_profile_json["_source"]))
#             #user_profile_json = json_normalize(user_profile_json)
#             user_row = []
#             #yes_user_data.append(json_normalize(user_profile_json), ignore_index = True)
#             df_rows.append(user_profile_json)
#             for key in user_profile_json:
#                 if key not in df_cols:
#                     #print key
#                     df_cols.append(key)
#                 #print user_profile_json[key]
#                 # if isinstance(user_profile_json[key], list):
#                 #     print user_profile_json[key]
#                 #     print "hi"
#             #     print key
#             #     print row_index
#             #     yes_user_data.loc[row_index,key] = user_profile_json[key]
#     #yes_user_data = pd.DataFrame(columns = df_cols)
#     yes_user_data = json_normalize(df_rows)
#     #print yes_user_data
#     #print df_rows
#     # for x in df_rows:
#     #     print x
#     #     yes_user_data.append(x, ignore_index = True)
#     print list(yes_user_data)
#     print len(list(yes_user_data))
#     print yes_user_data
