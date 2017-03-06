from flask import Flask, render_template, request, jsonify
import tweepy, json
import es_users
app = Flask(__name__)
ACCESS_TOKEN = ""
ACCESS_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
KEYWORDS = []

@app.route('/')
def student():
    result = es_users.getAllUserScreenNames()
    return render_template('user_profiles.html', result = result)

@app.route('/<user>')
def hello_name(user):
    result = es_users.getUser(user)
    tweets = es_users.getStoredTweets(user)
    return render_template('user_profile.html', user = result, tweets = tweets)

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return render_template("result.html", result = result)

if __name__ == '__main__':
   app.run(debug = True)





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
