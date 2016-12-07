import time

from eventDetectionFromTwitter.source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from eventDetectionFromTwitter.source.controller.EventDetection.OptimisedEventDetectorMEDBased import \
    OptimisedEventDetectorMEDBased

MIN_TERM_OCCURENCE=15
REMOVE_NOISE_WITH_POISSON_LAW=False

TIME_RESOLUTION=1800
DISTANCE_RESOLUTION=100
SCALE_NUMBER=4
MIN_SIMILARITY=0.8

#le nombre de tweets geolocalises
NUMBER_OF_TWEETS=35906

#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromJSONRepositoryAndSave(repositoryPath="C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromJSONRepository(repositoryPath)

#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromCSVRepositoryAndSave(repositoryPath="C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets\\smallTweets3.csv") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromCSVRepository(repositoryPath)

#---------------------------------------------------------------------------------------------------------------------------------------------
def main(limit=3000,minimalTermPerTweet=MIN_TERM_OCCURENCE,remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True) :
    mongoDBHandler = MongoDBHandler()
    #getTweetsFromCSVRepositoryAndSave("C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets\\smallTweets3.csv")
    staringTime = time.time()
    tweets = mongoDBHandler.getAllTweets(limit=limit)

    eventDetector = OptimisedEventDetectorMEDBased(tweets, timeResolution=TIME_RESOLUTION,
                                                   distanceResolution=DISTANCE_RESOLUTION, scaleNumber=SCALE_NUMBER,
                                                   minSimilarity=MIN_SIMILARITY)

    events = eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,
                                     remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)



    print("")
    print("-" * 40)
    print("{0} Event detected : ".format(len(events)))
    print("-" * 40)
    for event in events :
        print(event)
        print("*" * 80)
    elapsed_time=(time.time()-staringTime)
    print("-"*40)
    print("Elapsed time : {0}s".format(elapsed_time))
    print("-"*40)
#---------------------------------------------------------------------------------------------------------------------------------------------
#les 15000 premiers tweets correspondent au meme jour : le 16 septembre
main(limit=15185, minimalTermPerTweet=MIN_TERM_OCCURENCE)