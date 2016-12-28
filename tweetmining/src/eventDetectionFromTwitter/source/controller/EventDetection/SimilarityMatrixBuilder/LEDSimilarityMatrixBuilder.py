# cette classe hérite de SimilarityMatrixBuilder
# on construit une matrice de similarite de taille n x n
# on trouve en M[i,j] une valeur calculee egale a la somme des produits des frequences normalisées des termes en commun entre I et J
# uniquement si I et J sont consideres comme voisins - cad dans le meme cluster de densité et avec au moins un terme en commun -
# ATTENTION ON RETOURNE UNE MATRICE TRIANGULAIRE SUPERIEURE _ EVITE LA REDONDANCE DE LA SYMETRIE _

import numpy as np
from scipy.sparse import dok_matrix,coo_matrix
from sklearn.neighbors import NearestNeighbors
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from ..Utils.TFIDFUtilities import getTweetsTFIDFVectorAndNorm
from ..Utils.Constants import DEG_LATITUDE_IN_METER

class LEDSimilarityMatrixBuilder(SimilarityMatrixBuilder) :
    def __init__(self,timeThreshold,distanceThreshold) :
        """
        timeThreshold : time threshold in seconds
        distanceThreshold : distance threshold in meter
        """
		
		# seuil de temps et de distance 
        self.timeThreshold=timeThreshold
        self.distanceThreshold=distanceThreshold
		
    def build(self,tweets,minimalTermPerTweet=5, remove_noise_with_poisson_Law=False) :
        """
        Return an upper sparse triangular matrix of similarity j>i
        """
		# on recupere le temps, la distance et le nombre de tweets n que l'on va traiter
        timeThreshold=float(self.timeThreshold)
        distanceThreshold=float(self.distanceThreshold)
        numberOfTweets=len(tweets)

		# initialise M comme une matrice de dimension numberOfTweets x numberOfTweets contenant des floats
        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)
        print "      Calculating TF-IDF vectors ..."
		
		# on utilise ensuite la fonction du module Utils :
		# on obtient donc 
		# 	- TFIDFVectors qui contient donc pour chaque tweet un tableau qui contient pour chaque terme une valeur normalisée par rapport a ce tweet
		#		la valeur = (la frequence d'apparition de ce terme par rapport a ce tweet) x (le nombre d'occurence de ce terme) / racine carré de la somme des valeurs au carré
		#	- TweetPerTermMap qui stocke pour chaque terme, l'ensemble des tweets qui contenait ce terme
        TFIDFVectors,TweetPerTermMap=getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=minimalTermPerTweet, remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
        print "      Constructing similarity matrix ..."

		# http://scikit-learn.org/stable/modules/neighbors.html
		
		# -> transformation de la distance seuil en degres qui va permettre de classifier les tweets avec un calcul de densité locale
		# -> on met dans spatialIndex le resultat de cette classification pour chaque tweet dont on connait la latitude et la longitude
		# 	 spatialIndex est un objet complexe
		# on a bien un algo qui realise, a partir de n tweets :
		#	- un tableau d'indices qui contient tous les couples de tweets consideres comme voisins
		#	- un tableau de distance qui, pour chaque couple du tableau indices, contient la distance euclidienne entre les tweets de ce couple
		#	- on peut aussi construire une matrice d'adjacence de taille n x n 
        distanceThresholdInDegree=distanceThreshold/DEG_LATITUDE_IN_METER
        spatialIndex=NearestNeighbors(radius=distanceThresholdInDegree, algorithm='auto')
        spatialIndex.fit(np.array([(tweet.position.latitude,tweet.position.longitude) for tweet in tweets]))

        SHOW_RATE=100

        for i in range(numberOfTweets) :
            if (i%SHOW_RATE==0) : print "\t",i,";"
            
			# on recupere le tweet et l'ensemble des termes cités dans ce tweet
			# et on considere comme voisins d'un tweet, tous les tweets qui 
			# 		- ont au moins un terme en commun
			#		& 
			# 		- sont consideres comme voisins par l'algo NearestNeighbors
            tweetI,TFIDFVectorI=tweets[i],TFIDFVectors[i]
            neighboors=set()
            
            #Recuperation des voisins par mots (les tweets ayant au moins un term en commun)
            TFIDFVectorIKeySet=set(TFIDFVectorI)
            for term in TFIDFVectorIKeySet : neighboors|=TweetPerTermMap[term]

            #Recuperation des voisins en espace (les tweets dans le voisinage self.distanceThreshold)
            position=np.array([tweetI.position.latitude,tweetI.position.longitude]).reshape(-1,2)
            neighboors&=set(spatialIndex.radius_neighbors(position)[1][0])

			# on parcourt ensuite tous les voisins du tweet
			# si ce tweet J est antérieur a notre tweet de travail ou s'ils sont trop eloignes dans le temps on ne traite pas le tweet
			# si on le traite,on recupere le tweet J dans TFIDFVectors et on recupere les termes en commun entre I et J
			# et on definit comme similarite entre I et J, la somme des produits des frequences normalisées des termes en commun entre I et J
			# donc plus la similarite est elevee, plus il y a de termes en commun entre les deux tweets
			# inversement, plus la similarite est faible, moins il y a de termes en commun entre les deux tweets
            for j in neighboors :
                tweetJ=tweets[j]

                """
                Ignorer les tweets qui ne sont pas apres le tweetI
                Ignorer les tweets qui ne sont pas dans le voisinage temporelle du tweetI
                """
                if (j<=i or tweetJ.delay(tweetI)>self.timeThreshold) : continue
                
                TFIDFVectorJ=TFIDFVectors[j]
                TFIDFVectorJKeySet=set(TFIDFVectorJ)
                keysIntersection=TFIDFVectorIKeySet & TFIDFVectorJKeySet
                similarity=0
                for term in keysIntersection : similarity+=TFIDFVectorI[term]*TFIDFVectorJ[term]
                M[i,j]=similarity

        return coo_matrix(M)
