import re, math, numpy as np
from ....model.Position import DEG_LATITUDE_IN_METER
from Constants import *


# on renvoie - TFIDFVectors qui contient donc pour chaque tweet un tableau qui contient pour chaque terme une valeur normalisée par rapport a ce tweet
#				la valeur = (la frequence d'apparition de ce terme par rapport a ce tweet) x (le nombre d'occurence de ce terme) / racine carré de la somme des valeurs au carré
#			 - TweetPerTermMap qui stocke pour chaque terme, l'ensemble des tweets qui contenait ce terme
#
def getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=5, remove_noise_with_poisson_Law=False) :

	# on recupere le nombre de tweets, on crée deux Maps IDFVector & TweetPerTermMap et on crée un tableau TFVectors
	# on declare aussi des variables pour stocker le min et le max de la latitude et le min et le max de la longitude
	# TFVectors -> stocke pour chaque tweet, l'ensemble des termes presents ainsi que leur fréquence d'apparition relative au Tweet
	# IDFVector -> stocke pour chaque terme le nbr d'occurence
	# TweetPerTermMap -> stocke pour chaque terme, l'ensemble des tweets qui contenait ce terme
    numberOfTweets=len(tweets)
    TFVectors=[]
    IDFVector={}
    TweetPerTermMap={}
    minLat=maxLat=tweets[0].position.latitude
    minLon=maxLon=tweets[0].position.longitude

    i=0
    #TFVecrors construction
    for tweet in tweets :
        #---------------------------------------------------------------------------
        #      Text processing
        #---------------------------------------------------------------------------
        text=tweet.text
        #Convert to lower case
        text = text.lower()
        #Convert www.* or https?://* to ""
        text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',text)
        #Convert @username to ""
        text = re.sub('@[^\s]+','',text)
        #Remove additional white spaces
        text = re.sub('[\s]+', ' ', text)
        #trim
        text = text.strip('\'"')
        #split
        regex="|".join(DELIMITERS)
        terms=re.split(regex,text)

        TFVector={}
        numberOfTerms=len(terms)
        baseFrequency=1./numberOfTerms if (numberOfTerms>0) else 0
        for term in terms :
            if (len(term)<=TERM_MINIMAL_SIZE or len(term)>=TERM_MAXIMAL_SIZE) : continue
            try: TFVector[term] += baseFrequency
            except KeyError: TFVector[term] = baseFrequency
        
        TFVectors.append(TFVector)
        for term in TFVector :
            if term in IDFVector :
                IDFVector[term] += 1
                TweetPerTermMap[term].add(i)
            else : 
                IDFVector[term] = 1
                TweetPerTermMap[term] = set([i])

        #For estimating the total area for noise filtering
        if (tweet.position.latitude<minLat) : minLat=tweet.position.latitude
        elif (tweet.position.latitude>maxLat) : maxLat=tweet.position.latitude
        if (tweet.position.longitude<minLon) : minLon=tweet.position.longitude
        elif (tweet.position.longitude>maxLon) : maxLon=tweet.position.longitude
        
        i+=1

    totalArea=(maxLat-minLat)*(maxLon-minLon)*DEG_LATITUDE_IN_METER*DEG_LATITUDE_IN_METER

    #-----------------------------------------------------------------------
    """
    print "Before Filtering ..."
    print "Number of term : ", len(TweetPerTermMap)
    print "Number of non empty tweets : ",len([1 for tfv in TFVectors if len(tfv)>0])
    print "-"*40
    """
    #-----------------------------------------------------------------------

	# une fois TFVectors, IDFVector et TweetPerTermMap remplis :
    #IDFVector preparation and noisy terms filtering
	# on parcourt tous les termes contenus dans IDFVector (map avec le nbr d'occurences)
	# par defaut on ne supprime pas le terme en mettant termToDelete a Faux
	# si un terme apparait un nombre de fois inférieur a minimalTermPerTweet ou s'il suit une loi de Poisson
	# -> on le supprime de nos Map et tableau de traitement
    for term in IDFVector :
        termToDelete=False
        numberOfTweetOfThisTerm=IDFVector[term]
        
        #Eliminate term that appear less than minimalTermPerTweet
        if (numberOfTweetOfThisTerm<minimalTermPerTweet) : termToDelete=True
            
        #Eliminate terms that have poisson distribution in space
        elif (remove_noise_with_poisson_Law) :
            tweetsOfTerm=list(TweetPerTermMap[term])
            numberOfTweetsPerThres=[0]*len(S_FOR_FILTERING)
            for indiceI in range(numberOfTweetOfThisTerm) :
                tweetI=tweets[tweetsOfTerm[indiceI]]
                positionI=tweetI.position
                for indiceJ in range(indiceI+1,numberOfTweetOfThisTerm) :
                    tweetJ=tweets[tweetsOfTerm[indiceJ]]
                    positionJ=tweetJ.position
                    k=len(S_FOR_FILTERING)-1
                    distanceIJ=positionI.approxDistance(positionJ)
                    while (k>=0 and distanceIJ<=S_FOR_FILTERING[k]) :
                        numberOfTweetsPerThres[k]+=1
                        k-=1
            LValuesPerThres=[math.sqrt(((2*totalArea*numPerThres)/numberOfTweetOfThisTerm)/math.pi)-thres for thres,numPerThres in zip(S_FOR_FILTERING,numberOfTweetsPerThres)]
            meanLValue=sum(LValuesPerThres)/len(LValuesPerThres)
            if (meanLValue<THRESHOLD_FOR_FILTERING) : termToDelete=True

        #Delete term 
        if (termToDelete) :
            tweetsOfTerm=TweetPerTermMap[term]
            for i in tweetsOfTerm :
                TFVectorI=TFVectors[i]
                del TFVectorI[term]
            del TweetPerTermMap[term]
            continue

        #Preserve Term and MAJ IDFVector value
        IDFVector[term]=math.log(float(numberOfTweets)/IDFVector[term],10)

    #-----------------------------------------------------------------------
    """
    print "After Filtering ..."
    print "Number of term : ", len(TweetPerTermMap)
    print "Number of non empty tweets : ",len([1 for tfv in TFVectors if len(tfv)>0])
    print "-"*40
    """
    #-----------------------------------------------------------------------

    #Construct the normalized TFIDFVectors
	# TFIDFVector est une map vide
	# pour chaque tableau de tweet dans TFVectors
	# 	-> on recupere le terme et sa frequence d'apparition
	#			-> on calcule TFIDF = (la frequence d'apparition de ce terme par rapport a ce tweet) x (le nombre d'occurence de ce terme)
	#			-> on met cette valeur dans TFIDFVector
	# 			-> on ajoute a TFIDFVectorNorm TFIDF au carré
	#	   on a donc a la fin TFIDFVectorNorm = somme de TFIDF au carré pour le tweet de traitement
	#	   on calcule la racine carré pour avoir une norme relative au tweet et normaliser les valeurs de TFIDFVector
	# on agglomere tout dans TFIDFVectors qui contient donc pour chaque tweet un tableau qui contient pour chaque terme une valeur normalisée
    TFIDFVectors=[]
    for TFVector in TFVectors :
        TFIDFVector={}
        TFIDFVectorNorm=0
        for term,tf in TFVector.iteritems() :
            TFIDF=tf*IDFVector[term]
            TFIDFVector[term]=TFIDF
            TFIDFVectorNorm+=math.pow(TFIDF,2)
        TFIDFVectorNorm=math.sqrt(TFIDFVectorNorm)
        for term in TFIDFVector : TFIDFVector[term]/=TFIDFVectorNorm
        TFIDFVectors.append(TFIDFVector)
        
    return TFIDFVectors,TweetPerTermMap
