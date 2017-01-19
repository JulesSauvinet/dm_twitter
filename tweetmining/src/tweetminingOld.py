import glob
import os
import time
from datetime import timedelta, datetime

# on appelle MongoDBHandler pour tout ce qui concerne la connexion a la base de donnees
# on appelle OptimisedEventDetectorMEDBased pour ce qui concerne la construction de la matrice de similarite et la construction des clusters

from eventDetectionFromTwitter.source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from eventDetectionFromTwitter.source.controller.EventDetection.OptimisedEventDetectorMEDBased import \
    OptimisedEventDetectorMEDBased

#MIN_TERM_OCCURENCE_E -> pourcentage d'apparition d'un terme en fonction du nombre de tweet d'un cluster
#MIN_TERM_OCCURENCE -> nombre d'occurence minimal d'un terme
#ELASTICITY -> booleen pour savoir si on utilise MIN_TERM_OCCURENCE_E ou MIN_TERM_OCCURENCE
#REMOVE_NOISE_WITH_POISSON_LAW -> booleen pour savoir si on supprime les termes qui sont régis par une loi de Poisson
#GEOLOCALISATION -> booleen pour savoir pour si on fait des clusters de densité avant de faire des clusters de similarite

#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromJSONRepositoryAndSave(repositoryPath="..\\data") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromJSONRepository(repositoryPath)

#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromCSVRepositoryAndSave(repositoryPath="..\\data\\tweets5.csv") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromCSVRepository(repositoryPath)

#firstdate = "2015-07-21"
#firstdate = "2015-09-16"
#---------------------------------------------------------------------------------------------------------------------------------------------
def main(limit=3000, minimalTermPerTweet=MIN_TERM_OCCURENCE,
		minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,
		remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,
		printEvents=True, elasticity=ELASTICITY, geolocalisation=False) :

    # on charge les donnees du CSV dans MongoDB
    #getTweetsFromCSVRepositoryAndSave("..\\data\\smallTweets3_filtered.csv")

    sortieFile = open("clusterSansPreTraitement.txt","w")
    vizuFile = open("vizuFileSansPreTraitement.txt","w")
    vizuFile.write("date,duration,position,radius,userNumber,tweetsNumber,importantHashtags\n")
	
	# ----- on recupere tous les tweets de la base de MongoDB pour trouver la 1ere date et la derniere date ----- #
    mongoDBHandler = MongoDBHandler()
    tweetsAll = mongoDBHandler.getAllTweets(limit=limit)
    minTime = maxTime = tweetsAll[0].time
    for tweet in tweetsAll:
        if (tweet.time < minTime):
            minTime = tweet.time
        if (tweet.time > maxTime): 
            maxTime = tweet.time
    timeTotal = maxTime-minTime

    # blackList = {} on ne peut pas la remplir au d?but
    # pour toutes les dates de nos donnees dans MongoDB
        # on lance un premier clustering
    # on stocke dans un tableau tous les hashtags pertinents
    # on calcule le nbr d'occurence de chaque hashtags du tableau
    # si un hashtags apparait plus de x% --> la blackList    
    # pour toutes les dates de nos donnees dans MongoDB cad celle avec lesquelles on a fait le 1er clutering
        # on lance un second clustering
        # en prenant soin de ne pas garder dans les hashtags pertinents ceux qui sont dans la blackList
        
    for i in range(timeTotal.days+1):
        mongoDBHandler = MongoDBHandler()
        #date_1 = datetime.strptime(minTime, "%Y-%m-%d")
        end_date = minTime + timedelta(days=i)

        datestring = end_date.strftime('%Y-%m-%d')

        staringTime = time.time()
        tweets = mongoDBHandler.getAllTweetsOfDate(limit=limit,date=datestring)

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
#3000 tweets par jour environ sur sample

#first date : "2015-07-21", last : date="2015-11-16" TODO mieux
main(limit=NUMBER_OF_TWEETS, minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,elasticity=ELASTICITY,geolocalisation=GEOLOCALISATION)

#Ladresse du modularityoptimizer
#https://github.com/satijalab/seurat/blob/master/java/ModularityOptimizer.java
