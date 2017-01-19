import glob
import os
import time
from datetime import timedelta, datetime

# on appelle MongoDBHandler pour tout ce qui concerne la connexion a la base de donnees
# on appelle OptimisedEventDetectorMEDBased pour ce qui concerne la construction de la matrice de similarite et la construction des clusters
from datetime import datetime
from scipy import stats
from statsmodels.stats import gof
from operator import itemgetter

from eventDetectionFromTwitter.source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from eventDetectionFromTwitter.source.controller.EventDetection.OptimisedEventDetectorMEDBased import \
    OptimisedEventDetectorMEDBased
from testStat import filterTweets

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
def filterTweets(tweets, usersToDelete):
    tweetsFilter = []

    usersTweets = {}
    # on recupere tous les users et tous leur tweets
    for tweet in tweets:
        user = tweet.userId

        if user not in usersToDelete:
            try:
                usersTweets[user].append(tweet)
            except KeyError:
                usersTweets[user] = [tweet]

    # on recupere tous les intervalles de temps pour la loi geometrique
    for user, userTweets in usersTweets.iteritems():
        deleteUser = False
        if (len(userTweets) > 10):
            if user in usersToDelete:
                deleteUser = True

            if not deleteUser :
                timeInterval = {}
                nbrInterval = 0.0

                for i in range(len(userTweets) - 1):
                    for j in range(i + 1, len(userTweets)):
                        tweetTime = userTweets[j].time - userTweets[i].time
                        totalMin = round(tweetTime.total_seconds() / 60.0, 0)

                        if (totalMin < 0.0):
                            tweetTime = userTweets[i].time - userTweets[j].time
                            totalMin = round(tweetTime.total_seconds() / 60.0, 0)

                        try:
                            timeInterval[totalMin] += 1.0
                        except KeyError:
                            timeInterval[totalMin] = 1.0
                        nbrInterval += 1.0

                timeListDict = []

                for interval, occurence in timeInterval.iteritems():
                    timeListDict.append({"time" : interval, "occurence" : occurence})


                timeListSorted = sorted(timeListDict, key=itemgetter('occurence'), reverse=True)


                times = []
                idx = 1
                for val in timeListSorted:
                    occurence = val["occurence"]
                    time = val["time"]

                    for i in range(int(occurence)) :
                        times.append(idx)
                    idx+=1

                (x, pval,isGeom,msg) = gof.gof_chisquare_discrete(stats.geom, (0.23,), times, 0.05,'Geom')

                print "res geom", x,pval,isGeom,msg

                #geomrvs = stats.geom.rvs(0.20, size=45)
                #print "comp"
                #print sorted(geomrvs)
                #print times

                if (isGeom == True):
                    deleteUser = True

        if (not(deleteUser == True)):
            tweetsFilter.extend(userTweets)
        else :
            if user not in usersToDelete:
                usersToDelete.append(user)

    return (tweetsFilter,usersToDelete)


#---------------------------------------------------------------------------------------------------------------------------------------------
def main(limit=15000, minimalTermPerTweet=MIN_TERM_OCCURENCE,
		minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,
		remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,
		printEvents=True, elasticity=ELASTICITY, geolocalisation=False) :

    # on charge les donnees du CSV dans MongoDB
    #getTweetsFromCSVRepositoryAndSave("..\\data\\smallTweets3_filtered.csv")

    sortieFile = open("sortieFile.txt","w")
    vizuFile = open("vizuFile.txt","w")
    vizuFile.write("date,duration,position,radius,userNumber,tweetsNumber,importantHashtags\n")
	
	# ----- on recupere tous les tweets de la base de MongoDB pour trouver la 1ere date et la derniere date ----- #
    mongoDBHandler = MongoDBHandler()
    tweetsAll = mongoDBHandler.getAllTweets(limit=NUMBER_OF_ALL_TWEETS) #mongoDBHandler.getAllTweets(limit=1500000)
    minTime = maxTime = tweetsAll[0].time
    for tweet in tweetsAll:
        if (tweet.time < minTime):
            minTime = tweet.time
        if (tweet.time > maxTime): 
            maxTime = tweet.time
    timeTotal = maxTime-minTime

    totalEvent = []
    blackList = []
	
    # --------------------------------------- on fait un premier clustering ------------------------------------- #

    usersToDelete = []

    for i in range(20):#range(timeTotal.days+1):
        mongoDBHandler = MongoDBHandler()
        #date_1 = datetime.strptime(minTime, "%Y-%m-%d")
        end_date = minTime + timedelta(days=i)

        datestring = end_date.strftime('%Y-%m-%d')

        staringTime = time.time()
        tweets = mongoDBHandler.getAllTweetsOfDate(limit=limit,date=datestring)

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
	
    #avec SmallTweet trie on detecte 110 evenements    
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
        if freq > 0.15 :
            blackList.append(hashs)

    # ---------------------------------------- on fait un second clustering ------------------------------------- #
    for i in range(20): #range(timeTotal.days+1):
        mongoDBHandler = MongoDBHandler()
        end_date = minTime + timedelta(days=i)

        datestring = end_date.strftime('%Y-%m-%d')

        staringTime = time.time()
        tweets = mongoDBHandler.getAllTweetsOfDate(limit=limit,date=datestring)
        print "tweet before filter : ", len(tweets)
        tweets, usersToDelete = filterTweets(tweets, usersToDelete)
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

    for hashs in blackList :
        print hashs 
    vizuFile.close()
    sortieFile.close()    

    for f in glob.glob("output*.txt"):
        os.remove(f)
    for f in glob.glob("input*.txt"):
        os.remove(f)

    print "USERS DELETED BY FILTRAGE : "

    for user in usersToDelete :
        print user

    print "\n\n\n CLUSTERING FINI... :-)\n\n\n"
#---------------------------------------------------------------------------------------------------------------------------------------------
#3000 tweets par jour environ sur sample

#first date : "2015-07-21", last : date="2015-11-16" TODO mieux
MAX_NUMBER_BY_DAY = 30000
main(limit=30000, minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,elasticity=ELASTICITY,geolocalisation=GEOLOCALISATION)

#Ladresse du modularityoptimizer
#https://github.com/satijalab/seurat/blob/master/java/ModularityOptimizer.java
