from datetime import datetime
from scipy import stats
from statsmodels.stats import gof

from eventDetectionFromTwitter.source.model.Position import Position
from eventDetectionFromTwitter.source.model.Tweet import Tweet


def filterTweets(tweets):
    tweetsFilter = []

    usersTweets = {}
    # on recupere tous les users et tous leurs tweets dans une map
    for tweet in tweets:
        user = tweet.userId
        try:
            usersTweets[user].append(tweet)
        except KeyError:
            usersTweets[user] = [tweet]

    # on recupere tous les intervalles d'apparition des tweets pour un meme user
    for user, userTweets in usersTweets.iteritems():
        deleteUser = False
        timeInterval = {}
        nbrInterval = 0.0

		# on stocke dans une map tous les intervalles de temps d'apparition des tweets 
		# et le nombre de fois ou l'on publie avec ce meme intervalle de temps
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

		# on normalise aussi les donnees afin d'avoir un format de probabilite
        frequency = []
        for interval, occurence in timeInterval.iteritems():
            frequency.append(occurence / nbrInterval)

		# on trie par ordre decroissant afin de mettre en evidence une loi geometrique
        frequency = sorted(frequency, reverse=True)

        (x, pval,isGeom,msg) = gof.gof_chisquare_discrete(stats.geom, (0.25,), frequency, 0.25,'Geom')

        print "res"
        print x,pval,isGeom,msg

        if (isGeom == True):
            deleteUser = True

        if (not(deleteUser == True)):
            tweetsFilter.extend(userTweets)

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
    tweet8 = Tweet(123149, 11, "#test", "#hashtag", datetime(2015, 11, 10, 11, 10, 00), Position(-74.0, 43.06))
    tweet9 = Tweet(123410, 11, "#test", "#hashtag", datetime(2015, 11, 10, 11, 20, 00), Position(-74.0, 43.06))

    tweet10 = Tweet(223141, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 00), Position(-74.0, 43.06))
    tweet11 = Tweet(223142, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 02), Position(-74.0, 43.06))
    tweet12 = Tweet(223143, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 05), Position(-74.0, 43.06))
    tweet13 = Tweet(223144, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 10), Position(-74.0, 43.06))
    tweet14 = Tweet(223145, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 20), Position(-74.0, 43.06))
    tweet15 = Tweet(223146, 12, "#test", "#hashtag", datetime(2015, 11, 10, 10, 00, 50), Position(-74.0, 43.06))
    tweet16 = Tweet(223147, 12, "#test", "#hashtag", datetime(2015, 11, 10, 15, 00, 00), Position(-74.0, 43.06))
    tweet17 = Tweet(223148, 12, "#test", "#hashtag", datetime(2015, 11, 11, 10, 00, 00), Position(-74.0, 43.06))
    tweet18 = Tweet(223149, 12, "#test", "#hashtag", datetime(2015, 11, 11, 16, 00, 00), Position(-74.0, 43.06))
    tweet19 = Tweet(223410, 12, "#test", "#hashtag", datetime(2015, 11, 11, 20, 00, 00), Position(-74.0, 43.06))

    tweets = [tweet1, tweet2, tweet3, tweet4, tweet5, tweet6, tweet7, tweet8, tweet9, tweet0,
              tweet10, tweet11, tweet12, tweet13, tweet14, tweet15, tweet16, tweet17, tweet18, tweet19]

    return tweets

#tweets = fillTweets()
#tweetsFiltered = filterTweets(tweets)
#for t in tweetsFiltered:
#    print t
