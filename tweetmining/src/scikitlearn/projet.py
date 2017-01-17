print(__doc__)

import numpy as np

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
import scipy.sparse as ssp
from scipy.sparse import coo_matrix, vstack, hstack
import  scipy.stats as stats
import matplotlib.pyplot as plt
import csv
import pandas as pd
ALPHA = 2

df=pd.read_csv('smallTweets3.csv', sep=',')

coordinates = df.values[:,[6,7,9]]

coordinates = coordinates[coordinates[:,1] != "null"]
texts = coordinates[:,2]

coordinates=coordinates[:,[0,1]].astype(np.float)
rows = coordinates[:, 0] < -60

coordinates = coordinates[rows]
texts = texts[rows]
arr = np.arange(len(coordinates))

values = np.insert(coordinates,0,arr,axis=1)


print values
alpha=2
X = values[1:1500,]
#X = StandardScaler().fit_transform(X)

def distanceMetric(a,b):
    text1 = getTweets(a)
    text2 = getTweets(b)
    score = 1
    score = scoreText(text1,text2)
    return np.sqrt(np.sum((a[[1,2]]-b[[1,2]])**2))/(alpha**score)

def getTweets(a):
    index = int(a[0])
    identifiant = int(values[index,0])
    tweets = texts[identifiant]
    return tweets

def scoreText(a,b):
    if(not(isinstance(a, basestring)) or not(isinstance(b, basestring))):
        return 0
    if(a=="" or b==""):
        print a
        print b
    text1 = a.split()
    text2 = b.split()
    occ = 0
    for i in text1 :
        for j in text2 :
            if i==j:
                occ+=1
    return occ

db = DBSCAN(eps=0.3, min_samples=10,metric=distanceMetric,n_jobs=4).fit(X)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)


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
    plt.plot(xy[:, 1], xy[:, 2], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 1], xy[:, 2], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()


'''
from sklearn.feature_extraction.text import CountVectorizer
df = df.where((pd.notnull(df)), "")
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(df.values[:,9])
X_train_counts.shape
#localisation = df.values[:,6:8]
df2 = df.convert_objects(convert_numeric=True)
df2 = df2.values[:,6:8]
df2 = df2.astype(np.float)
col_mean = np.nanmean(df2,axis=0)
inds = np.where(np.isnan(df2))
df2[inds]=np.take(col_mean,inds[1])

array = hstack([df2,X_train_counts])

'''
