'''
Created on Jan 14, 2016

@author: Lu Chen
'''
from textblob import TextBlob
from dep_tool_class import Classifier
import pandas as pd
import sys



# campaign, and target entity
campaign_name = "election2016"

# targets = {"bernie_sanders", "donald_trump", "hillary_clinton", "john_kasich", "ted_cruz"}
target_name = "donald_trump"
# feature dimension
num_dim = 4000

# train data file
train_data_file = "../data/" + campaign_name + "/" + target_name + ".csv"
# model file
save_model = False
model_file = "models/symptoms/symptoms_SVM.pkl"

#__init__(self, train_data_file, model_file, num_dim = 4000):
cl = Classifier(train_data_file, model_file, num_dim)


tweet1 = "I WOULD TRUST DONALD J. TRUMP WITH MY LIFE, BUT NEVER THAT LYING DEVIOUS CORRUPT HILLARY CLINTON."
pred1 = cl.classify(tweet1)
print(pred1)

tweet2 = "RT @Lionheart0075: Donald Trump:Your Sons Love for Hunting African Animals Has Nothing to Do With the Second Amendment"
pred2 = cl.classify(tweet2)
#print(pred2)

tweet3 = "Here's How Donald Trump Wants to Fix Social Security #MakeDonaldDrumpfAgain"
pred3 = cl.classify(tweet3)
#print(pred3)

tweet4 = "Donald Trump Will Be The Death Of The Second Amendment"
pred4 = cl.classify(tweet4)
#print(pred4)


#train_data.columns = ['id', 'sentiment', 'content']

# data = pd.read_csv("clinton_Austin.csv")
# #print (data.sentiment)
# #sys.exit()
# for index,row in data.iterrows():
#     #print (data.content)
#     print (row['content'])
#     
#     print("human--->",row['sentiment'])
#     test_blob=TextBlob(str(row['content']))
#     print ("TextBlob----> ",test_blob.sentiment.polarity)
#     pred = cl.classify(str(row['content']))
#     print("predicted----> ",pred)
#     print ("--------------------------")


#sys.exit()

'''print ("-------4------------------------------------")
print (tweet4)
test_blob=TextBlob(tweet4)
print ("TextBlob----> ",test_blob.sentiment.polarity)
print("predicted----> ",pred4)


print ("-------3------------------------------")
print (tweet3)
test_blob=TextBlob(tweet3)
print ("TextBlob----> ",test_blob.sentiment.polarity)
print("predicted----> ",pred3)


print ("-------2-----------------------------------")
print (tweet2)
test_blob=TextBlob(tweet2)
print ("TextBlob----> ",test_blob.sentiment.polarity)
print("predicted----> ",pred2)

print ("-------1------------------------------------")
print (tweet1)
test_blob=TextBlob(tweet1)
print ("TextBlob----> ",test_blob.sentiment.polarity)
print("predicted----> ",pred1)
'''
