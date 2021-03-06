# module de configuration pour l'acces et la persistance de nos tuples dans MongoDB

import os

from datetime import datetime

from pymongo import MongoClient

from ...model.Tweet import Tweet
from ...model.Position import Position
from TransformationUtilities import getTweetFromJSONFile, getTweetFromCSVLine


class MongoDBHandler :
    def __init__(self,port=27017,database_name='Twitter') :
        self.client = MongoClient('localhost', port)
        self.db = self.client[database_name]

    def saveTweet(self,tweet) :
        collection = self.db['tweets']
        collection.insert(MongoDBHandler.getDocumentFromTweet(tweet))
        
    def saveTweets(self,tweets) :
        collection = self.db['tweets']
        collection.insert([MongoDBHandler.getDocumentFromTweet(tweet) for tweet in tweets])

    def getAllTweets(self,limit=50) :
        collection = self.db['tweets']
        documents=collection.find()[0:limit]
        tweets=[MongoDBHandler.getTweetFromDocument(document) for document in documents]
        #print "tweet3: ", tweets[3]
        return tweets

    def getAllTweetsOfDate(self,limit=50,date="2015-07-21") :
        collection = self.db['tweets']

        year = int(date.split("-")[0])
        month = int(date.split("-")[1])
        day = int(date.split("-")[2])

        start = datetime(year, month, day, 00, 00, 00)
        print "start ", start
        end = datetime(year, month, day, 23, 59, 59)
        print "end ", end

        documents=collection.find({"time" : {'$lt': end, '$gte': start}})[0:limit]

        tweets=[MongoDBHandler.getTweetFromDocument(document) for document in documents]
        #print "tweet3: ", tweets[3]
        return tweets

    def saveTweetsFromJSONRepository(self,jsonDirectoryPath,ensureHavePosition=True) :
        jsonFilePaths=os.listdir(jsonDirectoryPath)
        i=1
        for jsonFilePath in jsonFilePaths :
            if (i%100==0) : print(i)
            i+=1
            path=os.path.join(jsonDirectoryPath,jsonFilePath)
            try :
                tweet=getTweetFromJSONFile(path)
                if (not ensureHavePosition or tweet.position) : self.saveTweet(tweet)
            except ValueError :
                print(jsonFilePath)

    def saveTweetsFromCSVRepository(self,csvPath,ensureHavePosition=True) :
        with open(csvPath) as f:
            tweets = f.readlines()
            i = 0
            for tweetLine in tweets :
                if i != 0 :
                    try :
                        tweet=getTweetFromCSVLine(tweetLine)                        
                        #print tweet.position
                        if (not ensureHavePosition or tweet.position) : self.saveTweet(tweet)
                    except ValueError :
                        print tweet
                i += 1
            
        
    @staticmethod
    def getDocumentFromTweet(tweet) :
        dictionary={}
        dictionary["_id"]=tweet.id
        dictionary["userId"]=tweet.userId
        dictionary["text"]=tweet.text
        dictionary["hashtags"]=tweet.hashtags
        dictionary["time"]=tweet.time
        dictionary["position"]=None
        if (tweet.position) :
            dictionary["position"]=[tweet.position.latitude,tweet.position.longitude]
        return dictionary

    @staticmethod
    def getTweetFromDocument(document) :
        _id=document["_id"]
        userId=document["userId"]
        text=document["text"]
        hashtags=document["hashtags"]
        time=document["time"]
        position=None
        if (document["position"]) :
            position=Position(float(document["position"][0]),float(document["position"][1]))
        tweet = Tweet(_id,userId,text,hashtags,time,position)

        if (document["position"]) :
            tweet.lat = float(document["position"][0])
            tweet.long = float(document["position"][1])
        return tweet
        
        
        
        
        
        
   
        
