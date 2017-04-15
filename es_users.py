from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
import json
import requests, pigeo
es = Elasticsearch(['localhost:9201'])
#pigeo.load_model()
stored_tweetCounts = {}

def getAllCoordinates():
	a, users_with_status_coordinates = getAllUsers_WithCoordinates()
	b, users_with_status_coordinates = getAllUsers_WithTweets_WithCoordinates(users_with_status_coordinates)
	c, users_with_status_coordinates, not_found_places = getAllUsers_WithTweets_WithPlaces_WithoutCoordinates(users_with_status_coordinates)
	d, users_with_status_coordinates, not_found_places = getAllUsers_WithTweets_WithProfile_Location_WithoutCoordinates_and_WithoutPlaces(users_with_status_coordinates)
	print not_found_places
	e = a + b + c + d
	e.sort(key=lambda x: x['tweet_count'], reverse=True)
	f = getAllUsers_WithTweets_WithOutLocation_WithoutCoordinates_and_WithoutPlaces(users_with_status_coordinates)
	print len(e)
	return e, f

# All users whose last status had a tweet with a geo location
def getAllUsers_WithCoordinates():
    user_objs = []
    users_with_status_coordinates = []
    res_users = es.search(size = 1000, scroll = '3m', index="user_profiles", doc_type="Self_Reported_Profiles_40k", body={"query":{"bool":{"must":[{"match":{"status.lang":"en"}},{"match":{"lang":"en"}},{"exists":{"field":"status.geo.coordinates"}}]}},"size":100}, request_timeout=60)
    s_id = res_users['_scroll_id']
    scroll_size = res_users['hits']['total']
    all_users = res_users['hits']['hits']
    #print all_users
    #print len(all_users)
    while (scroll_size > 0):
        res_users = es.scroll(scroll_id = s_id, scroll = '3m' , request_timeout=160)
        s_id = res_users['_scroll_id']
        scroll_size = len(res_users['hits']['hits'])
        tweets = res_users['hits']['hits']
        all_users = all_users + tweets
        #print "scroll_size: " + str(scroll_size)
        #print len(all_tweets)
    #print len(all_users)
    u_o = {}
    for x in all_users:
		u_o["screen_name"] = str(x["_id"])
		users_with_status_coordinates.append(str(x["_id"]))
		u_o["user_img"] = str(x["_source"]["profile_image_url_https"]).replace("_normal", "")
		u_o["lat"] = x["_source"]["status"]["geo"]["coordinates"][0]
		u_o["lng"] = x["_source"]["status"]["geo"]["coordinates"][1]
		u_o["tweet_count"] = getStoredTweetCount(u_o["screen_name"])
		user_objs.append(u_o)
		u_o = {} 
    return user_objs, users_with_status_coordinates

def getAllUsers_WithTweets_WithCoordinates(users_with_status_coordinates):
	user_count = es.count(index="user_profiles", doc_type="Self_Reported_Profiles_40k")['count']
	res = es.search(index="depressed_tweets", doc_type="tweepyTweet", body={"_source": ["status.geo","user.profile_image_url_https"],"query":{"bool":{"must":[{"match":{"lang":"en"}},{"exists":{"field":"coordinates.coordinates"}}]}},"aggs":{"group_by_user":{"terms":{"field":"user.screen_name.keyword","size":200,"exclude":users_with_status_coordinates},"aggregations":{"hits":{"top_hits":{"size":1}}}}}}, request_timeout=60)
	all_users = res['aggregations']['group_by_user']['buckets']
	user_profs = []
	user_objs = []
	u_o = {}
	for x in all_users:
		y = x["hits"]["hits"]["hits"][0]["_source"]["user"]
		u_o["screen_name"] = str(x["key"])
		users_with_status_coordinates.append(str(x["key"]))
		u_o["user_img"] = str(x["hits"]["hits"]["hits"][0]["_source"]["user"]["profile_image_url_https"]).replace("_normal", "")
		u_o["lat"] = x["hits"]["hits"]["hits"][0]["_source"]["geo"]["coordinates"][0]
		u_o["lng"] = x["hits"]["hits"]["hits"][0]["_source"]["geo"]["coordinates"][1]
		u_o["tweet_count"] = getStoredTweetCount(u_o["screen_name"])
		u_o = {} 
	return user_objs, users_with_status_coordinates
	
def getAllUsers_WithTweets_WithPlaces_WithoutCoordinates(users_with_status_coordinates):
	user_count = es.count(index="user_profiles", doc_type="Self_Reported_Profiles_40k")['count']
	all_users = []
	res = es.search(index="depressed_tweets", doc_type="tweepyTweet", body={"query":{"bool":{"must_not":[{"exists":{"field":"coordinates.coordinates"}},{"exists":{"field":"location"}}],"must":[{"match":{"lang":"en"}},{"exists":{"field":"place.place_type"}}]}},"aggs":{"group_by_user":{"terms":{"field":"user.screen_name.keyword","size":20,"exclude":users_with_status_coordinates},"aggregations":{"hits":{"top_hits":{"size":1}}}}}}, request_timeout=160)
	result_tweet_count = res['hits']['total']
	all_users = res['aggregations']['group_by_user']['buckets']
	user_profs = []
	user_objs = []
	u_o = {}
	for x in all_users:
		city = str((x["hits"]["hits"]["hits"][0]["_source"]["place"]["full_name"]).encode("utf-8"))
		response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyDYRyuCbFOh_8ivTTnm1YjsXv4kKYWoPYc&address=' + city)
		resp_json_payload = response.json()
		not_found_places = []
		if len(resp_json_payload['results']) > 0:
			u_o["screen_name"] = str(x["key"])
			users_with_status_coordinates.append(str(x["key"]))
			u_o["user_img"] = str(x["hits"]["hits"]["hits"][0]["_source"]["user"]["profile_image_url_https"]).replace("_normal", "")
			u_o["lat"] = resp_json_payload['results'][0]['geometry']['location']["lat"]
			u_o["lng"] = resp_json_payload['results'][0]['geometry']['location']["lng"]
			u_o["tweet_count"] = getStoredTweetCount(u_o["screen_name"])
			user_objs.append(u_o)
			u_o = {} 
		else:
			not_found_places.append(str((x["hits"]["hits"]["hits"][0]["_source"]["place"]["full_name"]).encode("utf-8")))
		
	return user_objs, users_with_status_coordinates, not_found_places	

def getAllUsers_WithTweets_WithProfile_Location_WithoutCoordinates_and_WithoutPlaces(users_with_status_coordinates):
	user_count = es.count(index="user_profiles", doc_type="Self_Reported_Profiles_40k")['count']
	all_users = []
	res = es.search(index="user_profiles", doc_type="Self_Reported_Profiles_40k", body={"_source": ["profile_image_url_https"],"query":{"bool":{"must_not":[{"exists":{"field":"status.coordinates.coordinates"}},{"exists":{"field":"place.place_type"}},{"match":{"profile_location.full_name":""}}],"must":[{"match":{"lang":"en"}},{"exists":{"field":"profile_location"}}]}},"aggs":{"group_by_user":{"terms":{"field":"screen_name.keyword","size":20,"exclude":users_with_status_coordinates},"aggregations":{"hits":{"top_hits":{"size":1}}}}}}, request_timeout=160)
	result_tweet_count = res['hits']['total']
	all_users = res['aggregations']['group_by_user']['buckets']
	user_profs = []
	user_objs = []
	u_o = {}
	size = 1000
	scroll = '3m'
	scroll_size = res['hits']['total']
	tweets = all_users
	while (len(tweets) > 0):
		tweets = []
		res = es.search(index="user_profiles", doc_type="Self_Reported_Profiles_40k", body={"query":{"bool":{"must_not":[{"exists":{"field":"status.coordinates.coordinates"}},{"exists":{"field":"place.place_type"}},{"match":{"profile_location.full_name":""}}],"must":[{"match":{"lang":"en"}},{"exists":{"field":"profile_location"}}]}},"aggs":{"group_by_user":{"terms":{"field":"screen_name.keyword","size":20,"exclude":users_with_status_coordinates},"aggregations":{"hits":{"top_hits":{"size":1}}}}}}, request_timeout=160)
		tweets = res['aggregations']['group_by_user']['buckets']
		for x in tweets:
			users_with_status_coordinates.append(str(x["key"])) 
		all_users = all_users + tweets
		break
	for x in all_users:
		city = str((x["hits"]["hits"]["hits"][0]["_source"]["profile_location"]["full_name"]).encode("utf-8"))
		response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyDYRyuCbFOh_8ivTTnm1YjsXv4kKYWoPYc&address=' + city)
		resp_json_payload = response.json()
		not_found_places = []
		if len(resp_json_payload['results']) > 0:
			u_o["screen_name"] = str(x["key"])
			users_with_status_coordinates.append(str(x["key"]))
			u_o["user_img"] = str(x["hits"]["hits"]["hits"][0]["_source"]["profile_image_url_https"]).replace("_normal", "")
			u_o["lat"] = resp_json_payload['results'][0]['geometry']['location']["lat"]
			u_o["lng"] = resp_json_payload['results'][0]['geometry']['location']["lng"]
			u_o["tweet_count"] = getStoredTweetCount(u_o["screen_name"])
			user_objs.append(u_o)
			u_o = {} 
		else:
			not_found_places.append(str((x["hits"]["hits"]["hits"][0]["_source"]["profile_location"]["full_name"]).encode("utf-8")))		
	return user_objs, users_with_status_coordinates, not_found_places

def getAllUsers_WithTweets_WithOutLocation_WithoutCoordinates_and_WithoutPlaces(users_with_status_coordinates):
	user_count = es.count(index="user_profiles", doc_type="Self_Reported_Profiles_40k")['count']
	all_users = []
	res = es.search(index="depressed_tweets", doc_type="tweepyTweet", body={"_source": ["user.screen_name", "user.profile_image_url_https"],"query":{"bool":{"must_not":[{"exists":{"field":"coordinates.coordinates"}},{"exists":{"field":"location"}},{"exists":{"field":"profile_location"}},{"exists":{"field":"place.place_type"}}],"must":[{"match":{"lang":"en"}}]}},"aggs":{"group_by_user":{"terms":{"field":"user.screen_name.keyword","size":20,"exclude":users_with_status_coordinates},"aggregations":{"hits":{"top_hits":{"size":1}}}}}}, request_timeout=160)
	result_tweet_count = res['hits']['total']
	all_users = res['aggregations']['group_by_user']['buckets']
	user_profs = []
	user_objs = []
	u_o = {}
	size = 1000
	scroll = '3m'
	scroll_size = res['hits']['total']
	tweets = all_users
	while (len(tweets) > 0):
		tweets = []
		res = es.search(index="user_profiles", doc_type="Self_Reported_Profiles_40k",  body={"query":{"bool":{"must_not":[{"exists":{"field":"coordinates.coordinates"}},{"exists":{"field":"location"}},{"exists":{"field":"profile_location"}},{"exists":{"field":"place.place_type"}}],"must":[{"match":{"lang":"en"}}]}},"aggs":{"group_by_user":{"terms":{"field":"user.screen_name.keyword","size":20,"exclude":users_with_status_coordinates},"aggregations":{"hits":{"top_hits":{"size":1}}}}}}, request_timeout=160)
		tweets = res['aggregations']['group_by_user']['buckets']
		for x in tweets:
			if "status" in x["hits"]["hits"]["hits"][0]["_source"]:
				y = x["hits"]["hits"]["hits"][0]["_source"]["status"]["text"]
			users_with_status_coordinates.append(str(x["key"])) 
		all_users = all_users + tweets
		break
	#print len(all_users)
	for x in all_users:
		#print x["key"]
		pigeo_res = pigeo.geo(str('@' + x["key"]))
	# 	sys.exit()
		#print x
		u_o["screen_name"] = str(x["hits"]["hits"]["hits"][0]["_source"]["user"]["screen_name"])
		u_o["user_img"] = str(x["hits"]["hits"]["hits"][0]["_source"]["user"]["profile_image_url_https"]).replace("_normal", "")
		u_o["lat"] = pigeo_res["lat"]
		u_o["lng"] = pigeo_res["lon"]
		u_o["tweet_count"] = getStoredTweetCount(u_o["screen_name"])
		user_objs.append(u_o)
		u_o = {} 
	return user_objs

def getAllUserScreenNames():
    user_obj = []
    users_withTweets = []
    usersTweetCounts = []
    res_users = es.search(index="user_profiles", doc_type="Self_Reported_Profiles_40k", body={"query": {"exists": {"field": "status.geo.coordinates"}}, "size" : 100 }, request_timeout=360)
    res_users = res_users["hits"]["hits"]
    for user in res_users:
    	#print user["_source"]["status"]["geo"]["coordinates"]
    	z = {}
    	z["screen_name"] = user["_source"]["screen_name"]
    	z["tweet_count"] = getStoredTweetCount(user["_source"]["screen_name"])
    	z["user_object"] = user
    	user_obj.append(z)
    # res = res['aggregations']['group_by_tweets']['buckets']
#     #print res[0]
#     profiles = res
#     #print len(profiles)
# 
#     #print len(profiles)
#     for buckets in profiles:
#     	#print x
#     	#x = json.dumps(json.loads(x))
#     	profile = getUser(buckets['key'])
#     	#print y
#     	users_withTweets.append(profile[0])
#         #print getStoredTweetCount(x["key"])
#     	z = {}
#     	z["screen_name"] = buckets["key"]
#     	z["tweet_count"] = getStoredTweetCount(buckets["key"])
#     	z["user_object"] = profile[0]
#         #print profile[0]
#         #print z
#         user_obj.append(z)
#         usersTweetCounts.append(getStoredTweetCount(buckets["key"]))
#         # if getStoredTweetCount(x["key"]) > 25:
# #         	x = getUser(x)
# #         	users_withTweets.append(x)
# #         	print x
# #         	usersTweetCounts.append(getStoredTweetCount(x["_id"]))
# #             #print getStoredTweetCount(x["_id"])
    user_obj.sort(key=lambda x: x['tweet_count'], reverse=True)
    #print user_obj
    #users_withTweets.sort(key=lambda x: getStoredTweetCount(x['_id']), reverse=True)
    #print y
    #return users_withTweets, usersTweetCounts
    return user_obj

def getUser(screen_name):
    res = es.search(index="user_profiles", doc_type="Self_Reported_Profiles_40k", body={"query": { "match": {"_id" : screen_name}}}, request_timeout=60)
    #print res
    user = res['hits']["hits"]
    return user

def getStoredTweets(screen_name):
    res = es.search(size = 1000, scroll = '3m', index="depressed_tweets", doc_type="tweepyTweet", body={"query": { "match": {"user.screen_name": screen_name}}}, request_timeout=160)
    s_id = res['_scroll_id']
    scroll_size = res['hits']['total']
    #print res
    all_tweets = res['hits']['hits']
    while (scroll_size > 0):
        res = es.scroll(scroll_id = s_id, scroll = '3m' , request_timeout=160)
        s_id = res['_scroll_id']
        scroll_size = len(res['hits']['hits'])
        tweets = res['hits']['hits']
        all_tweets = all_tweets + tweets
        print "scroll_size: " + str(scroll_size)
    return all_tweets

def getStoredTweetsSize(screen_name, size):
    res = es.search(size = 10, index="depressed_tweets", doc_type="tweepyTweet", body={"query": { "match": {"user.screen_name": screen_name}}}, request_timeout=160)
    all_tweets = res['hits']['hits']
    return all_tweets

def parse_tweet_obj(screen_name):
	tweet_jsons = es_users.getStoredTweets(screen_name)
	all_user_tweet_obj = []
	tweet_obj = {}
	for tweet_json in tweet_jsons:
		tweet_json = json.loads(json.dumps(tweet_json))
		tweet_obj["es_id"] = tweet_json["_id"]
		tweet_obj["text"] = tweet_json["_source"]["text"]
		tweet_obj["created_at"] = tweet_json["_source"]["created_at"]
		tweet_obj["favorite_count"] = tweet_json["_source"]["favorite_count"]
		tweet_obj["retweet_count"] = tweet_json["_source"]["retweet_count"]
		tweet_obj["twitter_id_str"] = tweet_json["_source"]["id_str"]
		tweet_obj["lang"] = tweet_json["_source"]["lang"]
		if "place" in tweet_json["_source"]:
			tweet_obj["place"] = tweet_json["_source"]["place"]
		if "coordinates" in tweet_json:
			if "coordinates" in tweet_json["coordinates"]:
				tweet_obj["coordinates"] = tweet_json["coordinates"]["coordinates"]
		#print tweet_obj["text"]
		all_user_tweet_obj.append(tweet_obj)
	return all_user_tweet_obj

def getStoredTweetCount(screen_name):
    res = es.search(index="depressed_tweets", doc_type="tweepyTweet", body={"query": { "match": {"user.screen_name": screen_name}}}, request_timeout=60)
    #print res
    tweet_count = res['hits']['total']
    return tweet_count

def getMax_Id(screen_name):
    res = es.search(index="depressed_tweets", doc_type="tweepyTweet", body={"query": { "match": {"user.screen_name": screen_name}}}, request_timeout=60)
    #print("%d documents found" % res['hits']['total'])
    tweet_ids = []
    for doc in res['hits']['hits']:
        #print("%s) %s" % (doc['_id'], doc['_source']))
        id_str = (doc['_id'], doc['_source']['id_str'])
        #print ((int(id_str[1])))
        tweet_ids.append((int(id_str[1])))
    #print "Max", max(tweet_ids)
    return max(tweet_ids)

def getTweet(id_str):
    res = es.search(index = "depressed_tweets", doc_type = "tweepyTweet", body = {"query": { "match": {"id_str":id_str} } })
    tweet_count = res['hits']['total']
    return tweet_count

def indexTweet(tweet_json):
    res = es.index(index = "depressed_tweets", doc_type = "tweepyTweet", body = tweet_json)
    print res

def indexUser(index_id, user_profile_json):
    res = es.index(index = "user_profiles", doc_type = "Self_Reported_Profiles_40k", body = user_profile_json, id = index_id)
    print res
	
	#size = 1000, scroll = '3m', 
	#s_id = res['_scroll_id']
	#scroll_size = res['hits']['total']
	#print "Total hits " + str(len(res['hits']['hits']))
	#print res['hits']['total']
	# while (scroll_size > 0):
# 		res = es.scroll(scroll_id = s_id, scroll = '3m' , request_timeout=160)
# 		s_id = res['_scroll_id']
# 		scroll_size = len(res['hits']['hits'])
# 		print res
# 		tweets = res['aggregations']['group_by_user']['buckets']
# 		all_tweets = all_tweets + tweets
#         #print "scroll_size: " + str(scroll_size)
	#print len(all_users)
