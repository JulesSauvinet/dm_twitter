import glob
import os
import time
from datetime import timedelta, datetime

from eventDetectionFromTwitter.source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from eventDetectionFromTwitter.source.controller.EventDetection.OptimisedEventDetectorMEDBased import \
    OptimisedEventDetectorMEDBased

MIN_TERM_OCCURENCE_E=0.35
MIN_TERM_OCCURENCE=20
ELASTICITY=False
REMOVE_NOISE_WITH_POISSON_LAW=False

TIME_RESOLUTION=1800
DISTANCE_RESOLUTION=100
SCALE_NUMBER=4
MIN_SIMILARITY=0.6

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
def main(limit=3000,minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True,date="2015-07-21",elasticity=ELASTICITY) :

    #getTweetsFromCSVRepositoryAndSave("C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets\\smallTweets3.csv")
    #getTweetsFromCSVRepositoryAndSave("C:\\Users\\Marine\\dm_twitter\\tweetmining\\data\\smallTweets3.csv")

    sortieFile = open("sortieFile.txt","w")
    vizuFile = open("vizuFile.txt","w")

    vizuFile.write("date,duration,position,radius,userNumber,tweetsNumbert,importantHashtags\n")

    for i in range(120):
        mongoDBHandler = MongoDBHandler()
        date_1 = datetime.strptime(date, "%Y-%m-%d")
        end_date = date_1 + timedelta(days=i)

        datestring = end_date.strftime('%Y-%m-%d')

        staringTime = time.time()
        tweets = mongoDBHandler.getAllTweetsOfDate(limit=limit,date=datestring)

        if (tweets):
            if (len(tweets)>0) :

                print "date : ", datestring
                sortieFile.write("date : " + datestring)
                eventDetector = OptimisedEventDetectorMEDBased(tweets, timeResolution=TIME_RESOLUTION,
                                                               distanceResolution=DISTANCE_RESOLUTION, scaleNumber=SCALE_NUMBER,
                                                               minSimilarity=MIN_SIMILARITY)

                events = eventDetector.getEvents(datestring, minimalTermPerTweet=minimalTermPerTweet,minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
                                                 remove_noise_with_poisson_Law=remove_noise_with_poisson_Law,elasticity=ELASTICITY)

                if len(events) > 0:
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

                        vizuFile.write(event.outForVizu()+"\n")

                        sortieFile.write("********************************************************************************\n")
                    elapsed_time=(time.time()-staringTime)
                    print("-"*40)
                    print("Elapsed time : {0}s".format(elapsed_time))
                    print("-"*40)
                    sortieFile.write("----------------------------------------\n")
                    sortieFile.write("Elapsed time : {0}s".format(elapsed_time)+"\n")
                    sortieFile.write("----------------------------------------\n\n\n")

    vizuFile.close()
    sortieFile.close()
    for f in glob.glob("output*.txt"):
        os.remove(f)
    for f in glob.glob("input*.txt"):
        os.remove(f)
    print "\n\n\n CLUSTERING FINI... :-)\n\n\n"
#---------------------------------------------------------------------------------------------------------------------------------------------
#3000 tweets par jour environ sur sample

#first date : "2015-07-21", last : date="2015-16-11" TODO mieux
main(limit=NUMBER_OF_TWEETS, minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,date=firstdate,elasticity=ELASTICITY)

#Ladresse du modularityoptimizer
#https://github.com/satijalab/seurat/blob/master/java/ModularityOptimizer.java