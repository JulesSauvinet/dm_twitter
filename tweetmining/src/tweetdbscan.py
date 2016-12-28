import glob

print(__doc__)

import numpy as np

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
import glob
import os
import time
from datetime import timedelta, datetime
from eventDetectionFromTwitter.source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from eventDetectionFromTwitter.source.controller.EventDetection.OptimisedEventDetectorMEDBased import \
    OptimisedEventDetectorMEDBased

import matplotlib.pyplot as plt

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

'''
# IMPORT

charar = np.chararray((100000,19))
df=pd.read_csv('../data/smallTweets3.csv', sep=',')
df.values
print df.values
'''


# fonction de distance
def distanceCalc(a, b):
    # print "distance : ", np.sqrt((np.sum((a - b) ** 2)))
    return np.sqrt(np.sum((a - b) ** 2))
    # return np.sum((a-b)**2)


firstdate = "2015-07-21"
#firstdate = "2015-09-16"
#---------------------------------------------------------------------------------------------------------------------------------------------
def main(limit=3000,minimalTermPerTweet=MIN_TERM_OCCURENCE,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True,date="2015-07-21",elasticity=ELASTICITY) :

    #getTweetsFromCSVRepositoryAndSave("C:\\Users\\jules\\Documents\\documents\M2\\datamining\\datas\\tweets\\smallTweets3.csv")
    #getTweetsFromCSVRepositoryAndSave("C:\\Users\\Marine\\dm_twitter\\tweetmining\\data\\smallTweets3.csv")

    sortieFile = open("sortieFile.txt","w")

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

                tDB = []
                for tweet in tweets:
                    lat = tweet.lat
                    long = tweet.long

                    if (lat is not None):
                        if (long is not None):
                            posT = [lat,long]
                            tDB.append([posT])

                tDB = np.concatenate(tDB)
                print(tDB)

                sortieFile.write("date : " + datestring)

                X = StandardScaler().fit_transform(tDB)

                # utilisation de la fonction
                db = DBSCAN(eps=0.1, min_samples=10, metric=distanceCalc).fit(X)
                # db = DBSCAN(eps=0.3, min_samples=10).fit(X)
                core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
                core_samples_mask[db.core_sample_indices_] = True
                labels = db.labels_

                # Number of clusters in labels, ignoring noise if present.
                n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

                if (n_clusters_ > 1):
                    print('Estimated number of clusters: %d' % n_clusters_)
                #print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
                #print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
                #print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
                #print("Adjusted Rand Index: %0.3f"
                #      % metrics.adjusted_rand_score(labels_true, labels))
                #print("Adjusted Mutual Information: %0.3f"
                #      % metrics.adjusted_mutual_info_score(labels_true, labels))
                    print("Silhouette Coefficient: %0.3f"
                        % metrics.silhouette_score(X, labels))

                # Black removed and is used for noise instead.
                unique_labels = set(labels)
                colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
                for k, col in zip(unique_labels, colors):
                    if k == -1:
                        # Black used for noise.
                        col = 'k'

                    class_member_mask = (labels == k)

                    xy = X[class_member_mask & core_samples_mask]
                    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                             markeredgecolor='k', markersize=14)

                    xy = X[class_member_mask & ~core_samples_mask]
                    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                             markeredgecolor='k', markersize=6)

                plt.title('Estimated number of clusters: %d' % n_clusters_)
                plt.show()


                events = []

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


                        sortieFile.write("********************************************************************************\n")
                    elapsed_time=(time.time()-staringTime)
                    print("-"*40)
                    print("Elapsed time : {0}s".format(elapsed_time))
                    print("-"*40)
                    sortieFile.write("----------------------------------------\n")
                    sortieFile.write("Elapsed time : {0}s".format(elapsed_time)+"\n")
                    sortieFile.write("----------------------------------------\n\n\n")

    sortieFile.close()
    for f in glob.glob("output*.txt"):
        os.remove(f)
    for f in glob.glob("input*.txt"):
        os.remove(f)
    print "\n\n\n CLUSTERING FINI... :-)\n\n\n"
#---------------------------------------------------------------------------------------------------------------------------------------------
#3000 tweets par jour environ sur sample

#first date : "2015-07-21", last : date="2015-16-11" TODO mieux
main(limit=NUMBER_OF_TWEETS, minimalTermPerTweet=MIN_TERM_OCCURENCE
     ,minimalTermPerTweetElasticity=MIN_TERM_OCCURENCE_E,
     date=firstdate,elasticity=ELASTICITY)

