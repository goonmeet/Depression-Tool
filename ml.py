import json, es_users, sys, os, csv, Image, preprocess, re, pytesseract, sys
from TwitterAPI import *
from twitter import *
from time import sleep, time
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import urllib, cStringIO
import pytesseract
from textblob import TextBlob
reload(sys)
sys.setdefaultencoding('utf-8')

def modifiy_created_at(df):
	for index, row in df.iterrows():
		m = re.search('((\d{1,2})\/\d{1,2}\/\d{2,4}\ )(.+)', row["Created_at"])
		df.set_value(index,'Created_at',str(m.group(2) + " " + m.group(3)))
	return df

def add_cleanTweet_and_sentiment_to_df(df_b):
	print list(df_b)
	for index, row in df_b.iterrows():
		print index
		row["Cleaned_text"] = preprocess.preprocess_tweet(row["Raw_text"])
		print row["Cleaned_text"]
		if row["Cleaned_text"] is not "":
			row["Sentiment"] = sentiment(row["Cleaned_text"])
			print row["Sentiment"]
		else:
			row["Sentiment"] = 0
		df_b.loc[index] = row
	return df_b

def sentiment(tweet):
	blob = TextBlob(tweet)
	print (float(blob.sentiment.polarity))
	sum_senti = 0
	for sentence in blob.sentences:
		sum_senti = sum_senti + sentence.sentiment.polarity
		print sentence
	return float((sum_senti / len(blob.sentences)))

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
				tweet_obj["coordinates"] = tweet_json["coordinates"]["coordinates"]
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
		all_user_tweet_obj.append(tweet_obj)
		tweet_obj = {}
	#print len(all_user_tweet_obj)
	#Get all unique tweets:
	unique_tweets = []
	unique_tweets_obj = []
	for x in all_user_tweet_obj:
		#print x
		if x["text"] not in unique_tweets:
			unique_tweets_obj.append(x)
			unique_tweets.append(x["text"])
			#print len(unique_tweets_obj)
	all_user_tweet_obj = unique_tweets_obj
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

if __name__ == "__main__":
	#test_data = get_user_data(get_all_user_names_test())
	#print "Done with test data frame"
	# Read in goldstandard data
	df_a = pd.read_csv("alliwantisthin_goonmeet.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c' , names = ["Tweet_ID","Raw_text","Cleaned_text","Created_at","Sentiment","Annotation"])
	df_b = pd.read_csv("beyond_broken_jibril.csv", quotechar="\"", header = 0, error_bad_lines=False, engine='c', names = ["Tweet_ID","Raw_text","Cleaned_text","Created_at","Sentiment","Annotation"])
	df_c = pd.read_csv("beyond_darkness_ankia.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c', names = ["Tweet_ID","Raw_text","Cleaned_text","Created_at","Sentiment","Annotation"])
	df_d = pd.read_csv("suicidal_ideas_ankita.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c', names = ["Tweet_ID","Raw_text","Cleaned_text","Created_at","Sentiment","Annotation"])
	sum_senti = 0
	i = 0
	gold_df = df_a
	print len(gold_df)
	train_dfs = [df_b, df_c, df_d]
	for x in train_dfs:
		gold_df = gold_df.append(x, ignore_index=True)
		print len(gold_df)
	gold_df = modifiy_created_at(gold_df)
	#print gold_df
	#gold_df = gold_df.loc[gold_df["Annotation"] != "Other"]
	#print len(gold_df)
	#df_b.insert(1, "Cleaned_text", "hi")


# 		avg_sent = (sum_senti/len(blob.sentences) * 1.0)
# 		row['Sentiment'] = avg_sent
#     	print sum_senti
# 		user_profile_json = es_users.getUser(row[0])
# 		user_profile_json = es_users.getUser(row['USER_ID'])
# 		if len(user_profile_json) == 0:
# 			target.write(row[0]) #row['USER_ID']
# 			target.write("\n")
# 		
# 	train_dfs = [df_a, df_b, df_c, df_d]
# 	for x in train_dfs:
# 		d = x.loc[x["Annotation"] == "Other"]
# 		print d
	# yes_df = append(df_ric.loc[df_ric["DEPRESSED/NO"] == "yes"])
# 	print len(yes_df)
# 	yes_df_des = (df_des.loc[df_des["DEPRESSED/NO"] == "yes"])
# 	yes_df = yes_df.append(yes_df_des)
# 	print len(yes_df)
# 	df_old = pd.read_csv("depressed_users.csv", quotechar="\"", header = 0, error_bad_lines=False, encoding='utf-8', engine='c', names = ["DEPRESSED/NO"])
# 	yes_df = yes_df.append(df_old)
# 	print len(yes_df)
	
	
	
	#no_df =  df.loc[df['DEPRESSED/NO'] == "no"]
	# for index, row in yes_df.iterrows():
# 		print row[0]
# 		user_profile_json = es_users.getUser(row[0])
# # 		user_profile_json = es_users.getUser(row['USER_ID'])
# 		if len(user_profile_json) == 0:
# 			target.write(row[0]) #row['USER_ID']
# 			target.write("\n")
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

#	df_b.to_csv("check.csv", index = False, quotechar="\"", sep=',', header = 0 , columns = ["Tweet_ID","Raw_text","Cleaned_text","Created_at","Sentiment","Annotation"])
