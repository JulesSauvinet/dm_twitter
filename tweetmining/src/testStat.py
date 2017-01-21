from datetime import datetime
from scipy import stats
from statsmodels.stats import gof
from operator import itemgetter
import pandas as pd
import numpy as np

from eventDetectionFromTwitter.source.model.Position import Position
from eventDetectionFromTwitter.source.model.Tweet import Tweet

#determine
def filterTweets2(tweets1, tweets2):


    tweetsFilter = []

    usersTweets1 = {}
    usersTweets2 = {}
    # on recupere tous les users et tous leurs tweets dans une map
    for tweet in tweets1:
        user = tweet.userId
        try:
            usersTweets1[user].append(tweet)
        except KeyError:
            usersTweets1[user] = [tweet]

    for tweet in tweets2:
        user = tweet.userId
        try:
            usersTweets2[user].append(tweet)
        except KeyError:
            usersTweets2[user] = [tweet]



    # on recupere tous les intervalles d'apparition des tweets pour un meme user
    for user, userTweets1 in usersTweets1.iteritems():
        if (user in usersTweets2):
            userTweets2 = usersTweets2[user]
            #userTweets = sorted(userTweets, key=lambda tweet: (tweet.time-datetime(2015,7,1)).total_seconds())
            deleteUser = False
            timeInterval1 = []
            timeInterval2 = []
            #nbrInterval = 0.0

            # on stocke dans une map tous les intervalles de temps d'apparition des tweets
            # et le nombre de fois ou l'on publie avec ce meme intervalle de temps
            for i in range(len(userTweets1) - 1):
                #tweetTime1 = userTweets[i+1].time - userTweets[i].time
                tweetTime1 = userTweets1[i + 1].time
                timeInterval1.append(tweetTime1)

            for i in range(len(userTweets2) - 1):
                # tweetTime1 = userTweets[i+1].time - userTweets[i].time
                tweetTime2 = userTweets2[i + 1].time
                timeInterval2.append(tweetTime2)
                #totalMin = round(tweetTime.total_seconds() / 60.0, 0)


            print timeInterval1
            for i in range(len(timeInterval1)):
                timeInterval1[i]=(timeInterval1[i] -datetime(2015, 11, 1)).total_seconds()
            print timeInterval2
            for i in range(len(timeInterval2)):
                timeInterval2[i]=(timeInterval2[i] -datetime(2015,11, 1)).total_seconds()


            print timeInterval1
            print timeInterval2

            if (len(timeInterval1) == len(timeInterval2)):
                corr = stats.pearsonr(timeInterval1,timeInterval2)

                print corr

            isPears = False
            if (isPears == True):
                deleteUser = True

            if (not(deleteUser == True)):
                tweetsFilter.extend(userTweets1)



    return tweetsFilter

def fillTweets():
    tweet0 = Tweet(123141, 11, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 00), Position(-74.0, 43.06))
    tweet1 = Tweet(123142, 11, "#test", "#hashtag", datetime(2015, 11, 10, 10, 10, 00), Position(-74.0, 43.06))
    tweet2 = Tweet(123143, 11, "#test", "#hashtag", datetime(2015, 11, 10, 10, 20, 00), Position(-74.0, 43.06))
    tweet3 = Tweet(123144, 11, "#test", "#hashtag", datetime(2015, 11, 10, 10, 30, 00), Position(-74.0, 43.06))
    tweet4 = Tweet(123145, 11, "#test", "#hashtag", datetime(2015, 11, 10, 10, 40, 00), Position(-74.0, 43.06))
    tweet5 = Tweet(123146, 11, "#test", "#hashtag", datetime(2015, 11, 10, 10, 50, 00), Position(-74.0, 43.06))
    tweet6 = Tweet(123147, 11, "#test", "#hashtag", datetime(2015, 11, 10, 11, 00, 00), Position(-74.0, 43.06))
    tweet7 = Tweet(123148, 11, "#test", "#hashtag", datetime(2015, 11, 10, 11, 10, 00), Position(-74.0, 43.06))
    tweet8 = Tweet(123149, 11, "#test", "#hashtag", datetime(2015, 11, 10, 11, 20, 00), Position(-74.0, 43.06))
    tweet9 = Tweet(123410, 11, "#test", "#hashtag", datetime(2015, 11, 10, 11, 30, 00), Position(-74.0, 43.06))

    tweet10 = Tweet(223141, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 00), Position(-74.0, 43.06))
    tweet11 = Tweet(223142, 12, "#test", "#hashtag", datetime(2015, 11, 10, 13, 00, 02), Position(-74.0, 43.06))
    tweet12 = Tweet(223143, 12, "#test", "#hashtag", datetime(2015, 11, 10, 19, 00, 05), Position(-74.0, 43.06))
    tweet13 = Tweet(223144, 12, "#test", "#hashtag", datetime(2015, 11, 10, 20, 00, 10), Position(-74.0, 43.06))
    tweet14 = Tweet(223145, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 20), Position(-74.0, 43.06))
    tweet15 = Tweet(223146, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 50), Position(-74.0, 43.06))
    tweet16 = Tweet(223147, 12, "#test", "#hashtag", datetime(2015, 11, 10, 15, 42, 00), Position(-74.0, 43.06))
    tweet17 = Tweet(223148, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 00), Position(-74.0, 43.06))
    tweet18 = Tweet(223149, 12, "#test", "#hashtag", datetime(2015, 11, 10, 16, 00, 00), Position(-74.0, 43.06))
    tweet19 = Tweet(223410, 12, "#test", "#hashtag", datetime(2015, 11, 10, 20, 00, 00), Position(-74.0, 43.06))


    tweet20 = Tweet(123141, 11, "#test", "#hashtag", datetime(2015, 11, 11, 9, 00, 00), Position(-74.0, 43.06))
    tweet21 = Tweet(123142, 11, "#test", "#hashtag", datetime(2015, 11, 11, 10, 10, 00), Position(-74.0, 43.06))
    tweet22 = Tweet(123143, 11, "#test", "#hashtag", datetime(2015, 11, 11, 10, 20, 00), Position(-74.0, 43.06))
    tweet23 = Tweet(123144, 11, "#test", "#hashtag", datetime(2015, 11, 11, 10, 30, 00), Position(-74.0, 43.06))
    tweet24 = Tweet(123145, 11, "#test", "#hashtag", datetime(2015, 11, 11, 10, 40, 00), Position(-74.0, 43.06))
    tweet25 = Tweet(123146, 11, "#test", "#hashtag", datetime(2015, 11, 11, 10, 50, 00), Position(-74.0, 43.06))
    tweet26 = Tweet(123147, 11, "#test", "#hashtag", datetime(2015, 11, 11, 11, 00, 00), Position(-74.0, 43.06))
    tweet27 = Tweet(123148, 11, "#test", "#hashtag", datetime(2015, 11, 11, 11, 10, 00), Position(-74.0, 43.06))
    tweet28 = Tweet(123149, 11, "#test", "#hashtag", datetime(2015, 11, 11, 11, 20, 00), Position(-74.0, 43.06))
    tweet29 = Tweet(123410, 11, "#test", "#hashtag", datetime(2015, 11, 11, 15, 30, 00), Position(-74.0, 43.06))

    tweet210 = Tweet(223141, 12, "#test", "#hashtag", datetime(2015, 11, 11, 10, 00, 00), Position(-74.0, 43.06))
    tweet211 = Tweet(223142, 12, "#test", "#hashtag", datetime(2015, 11, 11, 13, 00, 02), Position(-74.0, 43.06))
    tweet212 = Tweet(223143, 12, "#test", "#hashtag", datetime(2015, 11, 11, 19, 00, 05), Position(-74.0, 43.06))
    tweet213 = Tweet(223144, 12, "#test", "#hashtag", datetime(2015, 11, 11, 18, 00, 10), Position(-74.0, 43.06))
    tweet214 = Tweet(223145, 12, "#test", "#hashtag", datetime(2015, 11, 11, 10, 00, 20), Position(-74.0, 43.06))
    tweet215 = Tweet(223146, 12, "#test", "#hashtag", datetime(2015, 11, 11, 19, 00, 50), Position(-74.0, 43.06))
    tweet216 = Tweet(223147, 12, "#test", "#hashtag", datetime(2015, 11, 11, 15, 42, 00), Position(-74.0, 43.06))
    tweet217 = Tweet(223148, 12, "#test", "#hashtag", datetime(2015, 11, 11, 10, 00, 00), Position(-74.0, 43.06))
    tweet218 = Tweet(223149, 12, "#test", "#hashtag", datetime(2015, 11, 11, 16, 00, 00), Position(-74.0, 43.06))
    tweet219 = Tweet(223410, 12, "#test", "#hashtag", datetime(2015, 11, 11, 21, 10, 00), Position(-74.0, 43.06))

    tweets = [tweet1, tweet2, tweet3, tweet4, tweet5, tweet6, tweet7, tweet8, tweet9, tweet0,
              tweet10, tweet11, tweet12, tweet13, tweet14, tweet15, tweet16, tweet17, tweet18, tweet19]


    tweets2 = [tweet21, tweet22, tweet23, tweet24, tweet25, tweet26, tweet27, tweet28, tweet29, tweet20,
              tweet210, tweet211, tweet212, tweet213, tweet214, tweet215, tweet216, tweet217]

    return tweets,tweets2

(tweets,tweets2) = fillTweets()
tweetsFiltered = filterTweets2(tweets,tweets2)
#for t in tweetsFiltered:
#    print t
