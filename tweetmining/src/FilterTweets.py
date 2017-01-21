from datetime import datetime
from scipy import stats
from statsmodels.stats import gof
from operator import itemgetter

from eventDetectionFromTwitter.source.model.Position import Position
from eventDetectionFromTwitter.source.model.Tweet import Tweet

class FilterTweets :

    # ---------------------------------------------------------------------------------------------------------------------------------------------
    # AVEC PEARSON
    def filterTweets2(self, tweets, usersToDelete):
        tweetsFilter = []

        usersTweets = {}
        # on recupere tous les users et tous leurs tweets dans une map
        for tweet in tweets:
            user = tweet.userId
            if user not in usersToDelete:
                try:
                    usersTweets[user].append(tweet)
                except KeyError:
                    usersTweets[user] = [tweet]

        # on recupere tous les intervalles d'apparition des tweets pour un meme user
        for user, userTweets in usersTweets.iteritems():
            deleteUser = False
            if (len(userTweets) > 5):
                if user in usersToDelete:
                    deleteUser = True

                if not deleteUser:
                    userTweets = sorted(userTweets,
                                        key=lambda tweet: (tweet.time - datetime(2015, 7, 1)).total_seconds())

                    timeInterval = {}
                    nbrInterval = 0.0

                    # on stocke dans une map tous les intervalles de temps d'apparition des tweets
                    # et le nombre de fois ou l'on publie avec ce meme intervalle de temps
                    for i in range(len(userTweets) - 1):
                        tweetTime = userTweets[i + 1].time - userTweets[i].time
                        totalMin = round(tweetTime.total_seconds() / 60.0, 0)

                        if (totalMin < 0.0):
                            tweetTime = userTweets[i].time - userTweets[i + 1].time
                            totalMin = round(tweetTime.total_seconds() / 60.0, 0)

                        try:
                            timeInterval[totalMin] += 1.0
                        except KeyError:
                            timeInterval[totalMin] = 1.0
                        nbrInterval += 1.0

                    timeListDict = []
                    for interval, occurence in timeInterval.iteritems():
                        timeListDict.append({"time": interval, "occurence": occurence})

                    timeListSorted = sorted(timeListDict, key=itemgetter('occurence'), reverse=True)

                    maxtime = timeListSorted[0]["time"]
                    maxoccurence = timeListSorted[0]["occurence"]

                    # print maxtime, maxoccurence
                    # print timeListSorted

                    times2 = []
                    idx = 1
                    for val in timeListSorted:
                        occurence = val["occurence"]
                        time = val["time"]

                        for i in range(int(occurence)):
                            times2.append(time)

                        idx += 1

                    times2Sorted = sorted(times2)

                    (x, pval, isPears, msg) = gof.gof_chisquare_discrete(stats.pearson3, (100, maxtime, 1),
                                                                         times2Sorted, 0.23, 'Pearson')

                    # print "res pearson", x,pval,isPears,msg

                    # pearsonrvs = stats.pearson3.rvs(50,maxtime, 1, size=9)
                    # print "comp"
                    # print sorted(pearsonrvs)
                    # print times2Sorted

                    if (isPears == True):
                        deleteUser = True

                    if (not (deleteUser == True)):
                        tweetsFilter.extend(userTweets)
                    else:
                        if user not in usersToDelete:
                            usersToDelete.append(user)

        return (tweetsFilter, usersToDelete)

    # ---------------------------------------------------------------------------------------------------------------------------------------------
    def filterTweets(self, tweets, usersToDelete):
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

                if not deleteUser:
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
                        timeListDict.append({"time": interval, "occurence": occurence})

                    timeListSorted = sorted(timeListDict, key=itemgetter('occurence'), reverse=True)

                    times = []
                    idx = 1
                    for val in timeListSorted:
                        occurence = val["occurence"]
                        time = val["time"]

                        for i in range(int(occurence)):
                            times.append(idx)
                        idx += 1

                    (x, pval, isGeom, msg) = gof.gof_chisquare_discrete(stats.geom, (0.23,), times, 0.05, 'Geom')

                    # print "res geom", x,pval,isGeom,msg

                    # geomrvs = stats.geom.rvs(0.20, size=45)
                    # print "comp"
                    # print sorted(geomrvs)
                    # print times

                    if (isGeom == True):
                        deleteUser = True

            if (not (deleteUser == True)):
                tweetsFilter.extend(userTweets)
            else:
                if user not in usersToDelete:
                    usersToDelete.append(user)

        return (tweetsFilter, usersToDelete)

    def filterTweets3(self, tweets1, tweets2, usersToDelete):
        tweetsFilter = []

        usersTweets1 = {}
        usersTweets2 = {}
        # on recupere tous les users et tous leurs tweets dans une map
        for tweet in tweets1:
            user = tweet.userId
            if user not in usersToDelete:
                try:
                    usersTweets1[user].append(tweet)
                except KeyError:
                    usersTweets1[user] = [tweet]

        for tweet in tweets2:
            user = tweet.userId
            if user not in usersToDelete:
                try:
                    usersTweets2[user].append(tweet)
                except KeyError:
                    usersTweets2[user] = [tweet]

        # on recupere tous les intervalles d'apparition des tweets pour un meme user
        for user, userTweets1 in usersTweets1.iteritems():
            deleteUser = False

            if (len(usersTweets1)>5) :
                if user in usersToDelete:
                    deleteUser = True

                if not deleteUser:
                    if (user in usersTweets2):
                        userTweets2 = usersTweets2[user]
                        # userTweets = sorted(userTweets, key=lambda tweet: (tweet.time-datetime(2015,7,1)).total_seconds())
                        timeInterval1 = []
                        timeInterval2 = []
                        # nbrInterval = 0.0

                        # on stocke dans une map tous les intervalles de temps d'apparition des tweets
                        # et le nombre de fois ou l'on publie avec ce meme intervalle de temps
                        for i in range(len(userTweets1) - 1):
                            # tweetTime1 = userTweets[i+1].time - userTweets[i].time
                            tweetTime1 = userTweets1[i + 1].time
                            timeInterval1.append(tweetTime1)

                        for i in range(len(userTweets2) - 1):
                            # tweetTime1 = userTweets[i+1].time - userTweets[i].time
                            tweetTime2 = userTweets2[i + 1].time
                            timeInterval2.append(tweetTime2)
                            # totalMin = round(tweetTime.total_seconds() / 60.0, 0)

                        for i in range(len(timeInterval1)):
                            timeInterval1[i] = (timeInterval1[i] - datetime(2015, 07, 1)).total_seconds()

                        for i in range(len(timeInterval2)):
                            timeInterval2[i] = (timeInterval2[i] - datetime(2015, 07, 1)).total_seconds()

                        mini = min(len(timeInterval1),len(timeInterval2))
                        if (mini > 5):
                            timeInterval1 = timeInterval1[0:mini]
                            timeInterval2 = timeInterval2[0:mini]
                            if (len(timeInterval1) == len(timeInterval2)):
                                corr = stats.pearsonr(timeInterval1, timeInterval2)
                                #print corr
                                if (corr >= 0.8):
                                    deleteUser = True

                        if (deleteUser == False):
                            tweetsFilter.extend(userTweets1)
                        else:
                            if user not in usersToDelete:
                                usersToDelete.append(user)

        return (tweetsFilter, usersToDelete)