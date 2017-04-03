from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
import json
es = Elasticsearch(['localhost:9201'])
    		#print user["_source"]["status"]["geo"]["coordinates"]

def parse_response(list_of_objs, type):
	all_obj = []
	if type == "user":
		for user in list_of_objs:
			z = {}
    		z["screen_name"] = user["_source"]["screen_name"]
    		z["tweet_count"] = getStoredTweetCount(user["_source"]["screen_name"])
    		z["user"] = user["_source"]
    		z["coordinates"] = user["_source"]["status"]["coordinates"]["coordinates"]
    		z["profile_image_url"] = user["_source"]["profile_image_url"]
    		z["lat"] = tweet_json["_source"]["status"]["geo"]["coordinates"][0]
    		z["lng"] = tweet_json["_source"]["status"]["geo"]["coordinates"][1]
    		if "place" in user["_source"]["status"]:
				z["place"] = user["_source"]["status"]["place"]
				location = True
    		all_obj.append(z)
	if type == "tweet":
		tweet_obj = {}
		for tweet_json in list_of_objs:
			location = False
			if "place" in tweet_json["_source"]:
				tweet_obj["place"] = tweet_json["_source"]["place"]
				location = True
			if "coordinates" in tweet_json:
				if "coordinates" in tweet_json["coordinates"]:
					tweet_obj["coordinates"] = tweet_json["coordinates"]["coordinates"]
					location = True
			if location:
				tweet_json = json.loads(json.dumps(tweet_json))
				tweet_obj["es_id"] = tweet_json["_id"]
				tweet_obj["text"] = tweet_json["_source"]["text"]
				tweet_obj["created_at"] = tweet_json["_source"]["created_at"]
				tweet_obj["favorite_count"] = tweet_json["_source"]["favorite_count"]
				tweet_obj["retweet_count"] = tweet_json["_source"]["retweet_count"]
				tweet_obj["twitter_id_str"] = tweet_json["_source"]["id_str"]
				tweet_obj["lang"] = tweet_json["_source"]["lang"]
				tweet_obj["screen_name"] = str(tweet_json["_source"]["user"]["screen_name"])
				tweet_obj["profile_image_url"] = tweet_json["_source"]["user"]["profile_image_url"]
    			tweet_obj["lat"] = tweet_json["_source"]["geo"]["coordinates"][0]
    			tweet_obj["lng"] = tweet_json["_source"]["geo"]["coordinates"][1]
    			all_obj.append(tweet_obj)
				#print tweet_obj["text"]

	return all_obj



def getAllTweetsWithCoordinates():
    res = es.search(size = 1000, scroll = '3m', index="depressed_tweets", doc_type="tweepyTweet", body={ "query": {"exists": {"field": "coordinates.coordinates"}}, "aggs": {"group_by_tweets": {"terms": {"field": "user.screen_name.keyword"}}}}, request_timeout=60)
    s_id = res['_scroll_id']
    scroll_size = res['hits']['total']
    all_tweets = res['hits']['hits']
    #print "Total hits " + str(len(res['hits']['hits']))
    #print res['hits']['total']
    while (scroll_size > 0):
        res = es.scroll(scroll_id = s_id, scroll = '3m' , request_timeout=160)
        s_id = res['_scroll_id']
        scroll_size = len(res['hits']['hits'])
        tweets = res['hits']['hits']
        all_tweets = all_tweets + tweets
        #print "scroll_size: " + str(scroll_size)
    print len(all_tweets)
    return all_tweets

def getAllUsersWithCoordinates():
    user_obj = []
    users_withTweets = []
    usersTweetCounts = []
    res_users = es.search(size = 1000, scroll = '3m', index="user_profiles", doc_type="Self_Reported_Profiles_40k", body={"query": {"exists": {"field": "status.geo.coordinates"}}, "size" : 100 }, request_timeout=60)
    s_id = res_users['_scroll_id']
    scroll_size = res_users['hits']['total']
    all_tweets = res_users['hits']['hits']
    while (scroll_size > 0):
        res_users = es.scroll(scroll_id = s_id, scroll = '3m' , request_timeout=160)
        s_id = res_users['_scroll_id']
        scroll_size = len(res_users['hits']['hits'])
        tweets = res_users['hits']['hits']
        all_tweets = all_tweets + tweets
        #print "scroll_size: " + str(scroll_size)
        #print len(all_tweets)
    print len(all_tweets)
    return all_tweets

def getAllCoordinates():
	a = parse_response(getAllUsersWithCoordinates(), "user")
	b = parse_response(getAllTweetsWithCoordinates(), "tweet")
	c = a + b
	return c

def getAllUserScreenNames():
    user_obj = []
    users_withTweets = []
    usersTweetCounts = []
    res = es.search(index="depressed_tweets", doc_type="tweepyTweet", body={ "query": {"exists": {"field": "coordinates.coordinates"}}, "aggs": {"group_by_tweets": {"terms": {"field": "user.screen_name.keyword"}}}}, request_timeout=60)
    res_users = es.search(index="user_profiles", doc_type="Self_Reported_Profiles_40k", body={"query": {"exists": {"field": "status.geo.coordinates"}}, "size" : 100 }, request_timeout=60)
    res_users = res_users["hits"]["hits"]
    for user in res_users:
    	#print user["_source"]["status"]["geo"]["coordinates"]
    	z = {}
    	z["screen_name"] = user["_source"]["screen_name"]
    	z["tweet_count"] = getStoredTweetCount(user["_source"]["screen_name"])
    	z["user_object"] = user
    	user_obj.append(z)
    res = res['aggregations']['group_by_tweets']['buckets']
    #print res[0]
    profiles = res
    #print len(profiles)

    #print len(profiles)
    for buckets in profiles:
    	#print x
    	#x = json.dumps(json.loads(x))
    	profile = getUser(buckets['key'])
    	#print y
    	users_withTweets.append(profile[0])
        #print getStoredTweetCount(x["key"])
    	z = {}
    	z["screen_name"] = buckets["key"]
    	z["tweet_count"] = getStoredTweetCount(buckets["key"])
    	z["user_object"] = profile[0]
        #print profile[0]
        #print z
        user_obj.append(z)
        usersTweetCounts.append(getStoredTweetCount(buckets["key"]))
        # if getStoredTweetCount(x["key"]) > 25:
#         	x = getUser(x)
#         	users_withTweets.append(x)
#         	print x
#         	usersTweetCounts.append(getStoredTweetCount(x["_id"]))
#             #print getStoredTweetCount(x["_id"])
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

# def getStoredTweets(screen_name, size):
#     res = es.search(index="depressed_tweets", doc_type="tweepyTweet", body={"query": { "match": {"user.screen_name": screen_name}}, "size" : size}, request_timeout=60)
#     #print res
#     tweets = res['hits']["hits"]
#     for x in tweets:
#     	x = json.dumps(x)
#     	x = json.loads(x)
#     	#print x["_source"]["coordinates"]
#     return tweets

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

#
# def get_all_tweets(screen_name):
#         #Twitter only allows access to a users most recent 3240 tweets with this method
#
#         auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#         auth.set_access_token(access_key, access_secret)
#         #authorize twitter, initialize tweepy
#         api = tweepy.API(auth)
#
#         #initialize a list to hold all the tweepy Tweets
#         alltweets = []
#
#         #make initial request for most recent tweets (200 is the maximum allowed count)
#         new_tweets = api.user_timeline(screen_name = screen_name,count=200)
#
#         #save most recent tweets
#         alltweets.extend(new_tweets)
#  oldest = alltweets[-1].id - 1
#
#         #keep grabbing tweets until there are no tweets left to grab
#         while len(new_tweets) > 0:
#                 print ("getting tweets before" + str(oldest))
#
#                 #all subsiquent requests use the max_id param to prevent duplicates
#                 new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
#
#                 #save most recent tweets
#                 alltweets.extend(new_tweets)
#
#                 #update the id of the oldest tweet less one
#                 oldest = alltweets[-1].id - 1
#
#                 print ("tweets downloaded so far " +str((len(alltweets))))
#
#         # Index using elastic search
#         return alltweets
#
#
# def read_self_reported_users(fin):
#         fin= "/home/amir/code/tweet_mappings/"+ fin
#         with open(fin, buffering=200000) as f:
#                 account_lists = []
#                 try:
#                         for line in f:
#                                 account = (line.split(',')[1]).strip()
#                                 account_lists.append(str(account))
#                         return account_lists
#                 except Exception as e:
#                         print(str(e))
#
# def indexTweets(tweets):
#
#     counter = 0
#
#     for tweet in tweets:
#
#         result = es.index(index=index_name, doc_type="tweepyTweet", body=tweet._json)
#
#         counter += 1
#
#         print (counter)
#
#
# # This gets the tweets and index them using elasticsearch
# def elasticIndexer():
#         fin =  "uniqueUsers.csv"
#         twitter_profiles = read_self_reported_users(fin)
#         #twitter_profiles=twitter_profiles[:100]
#         #print (twitter_profiles)
#         #sys.exit()
#         #twitter_profiles = ["grownhellokitty", "lovelovely_14", "caramel300"]
#
#         for i in range(len(twitter_profiles)):
#                 try:
#                         tweets = get_all_tweets(twitter_profiles[i])
#                         indexTweets(tweets)
#                         print (twitter_profiles[i] + "Done!")
#                         time.sleep(3)
#                 except:
#                         pass
#
#
# if __name__ == "__main__":
#
#     # index tweets
#     elasticIndexer()
