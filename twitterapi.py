'''
Created on 1 Apr 2016

@author: af
'''
import tweepy
from tweepy import OAuthHandler
import logging
import pdb

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

consumer_key = 'tp5SXyiRiyorRKeBzac5r9Ogr'
consumer_secret = 'OmtTzAlMgaOMMrcOquzyG9LxgMMOZytyyKeuYW6dYC7j5866PD'
access_token = '826535108727492608-omR6bQynLp03HWnR6qDavqXqTrACTKR'
access_token_secret = 'zxfCUuCBpoTx94EityJBcabeo9iOKLx0RClBvFTuWr1Ok'
# To get your own keys go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after        
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

  
def download_user_tweets(user_screen_name, count=100):
    logging.debug('downloading Twitter timeline of user ' + user_screen_name)
    timeline = []
    try:
        timeline = api.user_timeline(user_screen_name, count=count)
    except:
        logging.error('Note that the consumer_key, consumer_secret, access_token and access_secret should be set in tweet_downloader.py source file.')    
    return timeline

def download_user_tweets_iterable(user_screen_names, count=100):
    
    timelines = {}
    for user in user_screen_names:
        try:
            timeline = api.user_timeline(user, count=count)
            timelines[user] = timelines
        except:
            logging.error('Note that the consumer_key, consumer_secret, access_token and access_secret should be set in tweet_downloader.py source file.')
            

    return timelines

if __name__ == '__main__':
    timeline = download_user_tweets('@afshinray')