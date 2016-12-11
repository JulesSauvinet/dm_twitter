import time
import os,glob
from datetime import timedelta, datetime

import eventDetectionFromTwitter.source.model.Event
from eventDetectionFromTwitter.source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from eventDetectionFromTwitter.source.controller.EventDetection.OptimisedEventDetectorMEDBased import \
    OptimisedEventDetectorMEDBased

MIN_TERM_OCCURENCE=40
REMOVE_NOISE_WITH_POISSON_LAW=False

TIME_RESOLUTION=1800
DISTANCE_RESOLUTION=100
SCALE_NUMBER=4
MIN_SIMILARITY=0.8

#le nombre de tweets geolocalises
NUMBER_OF_TWEETS=35906

#---------------------------------------------------------------------------------------------------------------------------------------------
#def getTweetsFromJSONRepositoryAndSave(repositoryPath="C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets") :
def getTweetsFromJSONRepositoryAndSave(repositoryPath="C:\\Users\\Marine\\dm_twitter\\tweetmining\\data") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromJSONRepository(repositoryPath)

#---------------------------------------------------------------------------------------------------------------------------------------------
#def getTweetsFromCSVRepositoryAndSave(repositoryPath="C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets\\smallTweets3.csv") :
def getTweetsFromCSVRepositoryAndSave(repositoryPath="C:\\Users\\Marine\\dm_twitter\\tweetmining\\data\\smallTweets3.csv") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromCSVRepository(repositoryPath)

firstdate = "2015-07-21"
#firstdate = "2015-09-16"
#---------------------------------------------------------------------------------------------------------------------------------------------
def main(limit=3000,minimalTermPerTweet=MIN_TERM_OCCURENCE,remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True,date="2015-07-21") :

    #getTweetsFromCSVRepositoryAndSave("C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets\\smallTweets3.csv")
    getTweetsFromCSVRepositoryAndSave("C:\\Users\\Marine\\dm_twitter\\tweetmining\\data\\smallTweets3.csv")

    sortieFile = open("sortieFile.txt","w")
    
    for i in range(120):
        mongoDBHandler = MongoDBHandler()
        date_1 = datetime.strptime(date, "%Y-%m-%d")
        end_date = date_1 + timedelta(days=i)

        datestring = end_date.strftime('%Y-%m-%d')

        print "date : ", datestring
        sortieFile.write("date : " + datestring)
        staringTime = time.time()
        tweets = mongoDBHandler.getAllTweetsOfDate(limit=limit,date=datestring)

        if (tweets):
            if (len(tweets)>0) :
                eventDetector = OptimisedEventDetectorMEDBased(tweets, timeResolution=TIME_RESOLUTION,
                                                               distanceResolution=DISTANCE_RESOLUTION, scaleNumber=SCALE_NUMBER,
                                                               minSimilarity=MIN_SIMILARITY)

                events = eventDetector.getEvents(datestring, minimalTermPerTweet=minimalTermPerTweet,
                                                 remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)

                print("")     
                print("-" * 40)
                print("{0} Event detected : ".format(len(events)))
                print("-" * 40)
                sortieFile.write("\n")
                sortieFile.write("----------------------------------------\n")
                sortieFile.write("{0} Event detected : ".format(len(events))+"\n")
                sortieFile.write("----------------------------------------\n")
                
                for event in events :
                    print(event)
                    print("*" * 80)
                    sortieFile.write(event.__str__()+"\n")
                    sortieFile.write("********************************************************************************\n")
                elapsed_time=(time.time()-staringTime)
                print("-"*40)
                print("Elapsed time : {0}s".format(elapsed_time))
                print("-"*40)
                sortieFile.write("----------------------------------------\n")
                sortieFile.write("Elapsed time : {0}s".format(elapsed_time)+"\n")
                sortieFile.write("----------------------------------------\n\n\n\n")

    sortieFile.close()
    for f in glob.glob("output*.txt"):
        os.remove(f)
    for f in glob.glob("input*.txt"):
        os.remove(f)
#---------------------------------------------------------------------------------------------------------------------------------------------
#3000 tweets par jour environ sur sample

#first date : "2015-07-21", last : date="2015-16-11" TODO mieux
main(limit=NUMBER_OF_TWEETS, minimalTermPerTweet=MIN_TERM_OCCURENCE,date=firstdate)
