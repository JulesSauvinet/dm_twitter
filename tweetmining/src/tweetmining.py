import glob
import os
import time
from datetime import timedelta, datetime
from scipy import stats
from statsmodels.stats import gof
from operator import itemgetter

# on appelle MongoDBHandler pour tout ce qui concerne la connexion a la base de donnees
# on appelle OptimisedEventDetectorMEDBased pour ce qui concerne la construction de la matrice de similarite et la construction des clusters
from eventDetectionFromTwitter.source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from FilterTweets import FilterTweets
from eventDetectionFromTwitter.source.controller.EventDetection.OptimisedEventDetectorMEDBased import \
    OptimisedEventDetectorMEDBased

#MIN_TERM_OCCURENCE_E -> pourcentage d'apparition d'un terme en fonction du nombre de tweet d'un cluster
#MIN_TERM_OCCURENCE -> nombre d'occurence minimal d'un terme
#ELASTICITY -> booleen pour savoir si on utilise MIN_TERM_OCCURENCE_E ou MIN_TERM_OCCURENCE
#REMOVE_NOISE_WITH_POISSON_LAW -> booleen pour savoir si on supprime les termes qui sont regis par une loi de Poisson
#GEOLOCALISATION -> booleen pour savoir pour si on fait des clusters de densite avant de faire des clusters de similarite

MIN_TERM_OCCURENCE_E=0.2
MIN_TERM_OCCURENCE=20
ELASTICITY=False
REMOVE_NOISE_WITH_POISSON_LAW=False
GEOLOCALISATION=False

TIME_RESOLUTION=1800
DISTANCE_RESOLUTION=100
SCALE_NUMBER=4
MIN_SIMILARITY=0.6
DISTANCE_THRESHOLD=1000

#le nombre de tweets geolocalises
NUMBER_OF_TWEETS=35906
NUMBER_OF_ALL_TWEETS = 1183142

#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromJSONRepositoryAndSave(repositoryPath="..\\data") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromJSONRepository(repositoryPath)

#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromCSVRepositoryAndSave(repositoryPath="..\\data\\smallTweets3_filtered.csv") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromCSVRepository(repositoryPath)

#---------------------------------------------------------------------------------------------------------------------------------------------
def sansPreTraitement(limit=3000, minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,
                    remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True, elasticity=ELASTICITY, geolocalisation=False) :

    sortieFile = open("_clusterSansPreTraitement.txt","w")
    vizuFile = open("_vizuFileSansPreTraitement.txt","w")
    vizuFile.write("date,duration,position,radius,userNumber,tweetsNumber,importantHashtags\n")
	
    # ----- on recupere tous les tweets de la base de MongoDB pour trouver la 1ere date et la derniere date ----- #
    mongoDBHandler = MongoDBHandler()
    tweetsAll = mongoDBHandler.getAllTweets(limit=100000)
    minTime = maxTime = tweetsAll[0].time
    for tweet in tweetsAll:
        if (tweet.time < minTime):
            minTime = tweet.time
        if (tweet.time > maxTime): 
            maxTime = tweet.time
    timeTotal = maxTime-minTime
        
    for i in range(timeTotal.days+1):
        mongoDBHandler = MongoDBHandler()
        end_date = minTime + timedelta(days=i)

        datestring = end_date.strftime('%Y-%m-%d')

        staringTime = time.time()
        tweets = mongoDBHandler.getAllTweetsOfDate(limit=30000,date=datestring)

        if (tweets):
            if (len(tweets)>0) :

                print "date : ", datestring
                sortieFile.write("date : " + datestring)
                
                eventDetector = OptimisedEventDetectorMEDBased(tweets, timeResolution=TIME_RESOLUTION,
                                                               distanceResolution=DISTANCE_RESOLUTION, scaleNumber=SCALE_NUMBER,
                                                               minSimilarity=MIN_SIMILARITY, distanceThreshold=DISTANCE_THRESHOLD)

                events = eventDetector.getEvents(datestring, minimalTermPerTweet=minimalTermPerTweet,
                                                 minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
                                                 remove_noise_with_poisson_Law=remove_noise_with_poisson_Law,
                                                 elasticity=elasticity, geolocalisation=geolocalisation)

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
                else :
                    print("")
                    print("-" * 40)
                    print("0 Event detected : ")
                    print("-" * 40)
                    sortieFile.write("\n")
                    sortieFile.write("----------------------------------------\n")
                    sortieFile.write("0 Event detected : \n")
                    sortieFile.write("----------------------------------------\n")
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
def main(limit=30000, minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,
	remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True, elasticity=ELASTICITY, geolocalisation=False) :
    
    # on charge les donnees du CSV dans MongoDB
    # getTweetsFromCSVRepositoryAndSave("..\\data\\tweets5.csv")

    print "CHARGEMENT DES DONNEES FINI\n\n"

    #sansPreTraitement(limit=30000, minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,
    #                remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True, elasticity=ELASTICITY, geolocalisation=False)

    sortieFile = open("_clusterAvecTraitement.txt","w")
    blacklistFile = open("_blackList.txt","w")
    userDeletedFile = open("_userDeleted.txt","w")
    vizuFile = open("_vizuFileAvecTraitement.txt","w")
    vizuFile.write("eventId,date,duration,position,radius,userNumber,tweetsNumber,importantHashtags\n")

    ft = FilterTweets()

    # ----- on recupere tous les tweets de la base de MongoDB pour trouver la 1ere date et la derniere date ----- #
    mongoDBHandler = MongoDBHandler()
    tweetsAll = mongoDBHandler.getAllTweets(limit=100000) #mongoDBHandler.getAllTweets(limit=NUMBER_OF_ALL_TWEETS)
    minTime = maxTime = tweetsAll[0].time
    for tweet in tweetsAll:
        if (tweet.time < minTime):
            minTime = tweet.time
        if (tweet.time > maxTime):
            maxTime = tweet.time
    timeTotal = maxTime-minTime

    totalEvent = []
    blackList = []
    usersToDelete = []
	
    # --------------------------------------- on fait un premier clustering ------------------------------------- #

    usersToDelete = []

    for i in range(40,60): #range(10):#
        end_date = minTime + timedelta(days=i)
        datestring = end_date.strftime('%Y-%m-%d')
        staringTime = time.time()
        
        tweets = mongoDBHandler.getAllTweetsOfDate(limit=30000,date=datestring)

        if (tweets):
            if (len(tweets)>0) :

                print "date : ", datestring
                
                eventDetector = OptimisedEventDetectorMEDBased(tweets, timeResolution=TIME_RESOLUTION,
                                                               distanceResolution=DISTANCE_RESOLUTION, scaleNumber=SCALE_NUMBER,
                                                               minSimilarity=MIN_SIMILARITY, distanceThreshold=DISTANCE_THRESHOLD)

                events = eventDetector.getEvents(datestring, minimalTermPerTweet=minimalTermPerTweet,
                                                 minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
                                                 remove_noise_with_poisson_Law=remove_noise_with_poisson_Law,
                                                 elasticity=elasticity, geolocalisation=geolocalisation,blackList=blackList)

                if len(events) > 0:
                    totalEvent.extend(events)

    # ----------------------------------------- fin du premier clustering --------------------------------------- #
    
    # ---------------------------------------- remplissage de la blackList -------------------------------------- #
    numberOfEvent = float(len(totalEvent))
    pertinentHashtag = {}
    numberOfHash = 0

    # on enregistre tous les hashtags avec leur nbr d'occurence
    for event in totalEvent :
        hashtagsEvent = event.importantHashtags
        for hashs in hashtagsEvent :
            try:
                 pertinentHashtag[hashs] += 1.0
            except KeyError:
                pertinentHashtag[hashs] = 1.0
                numberOfHash += 1

    # on calcule la frequence d'apparition
    for hashs,occurence in pertinentHashtag.iteritems() :
        freq = occurence/numberOfEvent
        if freq > 0.125 :
            blackList.append(hashs)

    # -------------------------------------- fin remplissage de la blackList ------------------------------------ #
    
    # ---------------------------------------- on fait un second clustering ------------------------------------- #


    for i in range(40,60): #range(10):#
        end_date = minTime + timedelta(days=i)

        datestring = end_date.strftime('%Y-%m-%d')

        staringTime = time.time()

        tweets = mongoDBHandler.getAllTweetsOfDate(limit=limit,date=datestring)

        end_date2 = minTime + timedelta(days=i+1)
        datestring2 = end_date2.strftime('%Y-%m-%d')
        tweets2 = mongoDBHandler.getAllTweetsOfDate(limit=limit, date=datestring2)

        if (i != timeTotal.days):
            tweets, usersToDelete = ft.filterTweets3(tweets, tweets2, usersToDelete)

        print "tweet before filter : ", len(tweets)
        tweets, usersToDelete = ft.filterTweets(tweets, usersToDelete)
        print "tweet after filter : ", len(tweets)
        if (tweets):
            if (len(tweets)>0) :

                print "date : ", datestring
                sortieFile.write("date : " + datestring)

                eventDetector = OptimisedEventDetectorMEDBased(tweets, timeResolution=TIME_RESOLUTION,
                                                            distanceResolution=DISTANCE_RESOLUTION, scaleNumber=SCALE_NUMBER,
                                                            minSimilarity=MIN_SIMILARITY, distanceThreshold=DISTANCE_THRESHOLD)

                events = eventDetector.getEvents(datestring, minimalTermPerTweet=minimalTermPerTweet,
                                                 minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
                                                 remove_noise_with_poisson_Law=remove_noise_with_poisson_Law,
                                                 elasticity=elasticity, geolocalisation=geolocalisation, blackList=blackList)

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
                else :
                    print("")
                    print("-" * 40)
                    print("No Events detected : ")
                    print("-" * 40)
                    sortieFile.write("\n")
                    sortieFile.write("----------------------------------------\n")
                    sortieFile.write("No Events detected : \n")
                    sortieFile.write("----------------------------------------\n")
                    elapsed_time=(time.time()-staringTime)
                    print("-"*40)
                    print("Elapsed time : {0}s".format(elapsed_time))
                    print("-"*40)
                    sortieFile.write("----------------------------------------\n")
                    sortieFile.write("Elapsed time : {0}s".format(elapsed_time)+"\n")
                    sortieFile.write("----------------------------------------\n\n\n")

    print "\n\nUSERS DELETED BY FILTRAGE : "
    for user in usersToDelete :
        print user
        userDeletedFile.write(user+"\n")
    print "\n\nBLACKLIST : "
    for hashs in blackList :
        print hashs
        blacklistFile.write(hashs+"\n")
    vizuFile.close()
    sortieFile.close()
    blacklistFile.close()
    userDeletedFile.close()

    for f in glob.glob("output*.txt"):
        os.remove(f)
    for f in glob.glob("input*.txt"):
        os.remove(f)

    print "\n\n\nCLUSTERING FINI... :-)\n\n\n"
#---------------------------------------------------------------------------------------------------------------------------------------------
#3000 tweets par jour environ sur sample

#first date : "2015-07-21", last : date="2015-11-16" TODO mieux
MAX_NUMBER_BY_DAY = 30000
main(limit=30000, minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,elasticity=ELASTICITY,geolocalisation=GEOLOCALISATION)

#Ladresse du modularityoptimizer
#https://github.com/satijalab/seurat/blob/master/java/ModularityOptimizer.java
