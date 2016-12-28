# cette classe hérite de SimilarityMatrixBuilder
# il y a une tranformation de Haar qui est réalisée ------> comprendre pourquoi et a quoi elle sert
# on construit une matrice de similarite de taille n x n
# on trouve en M[i,j] une valeur calculee egale a 
#	- la somme des produits des frequences normalisées des termes en commun entre I et J
#	MULTIPLIE PAR
#	- un semblant de coefficient de correlation entre I et J
# uniquement si I et J sont consideres comme voisins - cad avec au moins un terme en commun -
# ATTENTION ON RETOURNE UNE MATRICE TRIANGULAIRE SUPERIEURE _ EVITE LA REDONDANCE DE LA SYMETRIE _

import math,re,numpy as np
from scipy.sparse import dok_matrix,coo_matrix
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from ....model.Position import Position
from ..Utils.Constants import *

class MEDSimilarityMatrixBuilder(SimilarityMatrixBuilder) :
    def __init__(self,timeResolution=1800,distanceResolution=100,scaleNumber=4,minSimilarity=0.5) :
        """
        timeResolution : define the time resolution for time series
        distanceResolution : define a cell size in meter (not exact)
        scaleNumber : nscale in the paper
        """
        self.timeResolution=timeResolution
        self.distanceResolution=distanceResolution
        self.scaleNumber=scaleNumber
        self.minSimilarity=max(min(minSimilarity,1),0)
        
    def build(self,tweets,minimalTermPerTweet=5, remove_noise_with_poisson_Law=False) :
        """
        Return an upper sparse triangular matrix of similarity j>i
        """
		# on recupere la résolution temporale, la résolution de distance, une echelle et le pourcentage de similarité
        timeResolution=self.timeResolution
        distanceResolution=self.distanceResolution
        scaleNumber=self.scaleNumber
        minSimilarity=self.minSimilarity
        
		# on construit une matrice n x n qui contiendra des float
        numberOfTweets=len(tweets)
        floatNumberOfTweets=float(numberOfTweets)
        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)
        deltaDlat=float(distanceResolution)/DEG_LATITUDE_IN_METER
        deltaDlon=float(distanceResolution)/DEG_LATITUDE_IN_METER
        print "\t\tPass 1 - Get General Information"
        #Pass 1 - Get General Information
		# on va recuperer la date de debut et la date de fin des tweets, ainsi que la latitude et longitude min et max des tweets
        minTime=maxTime=tweets[0].time
        minLat=maxLat=tweets[0].position.latitude
        minLon=maxLon=tweets[0].position.longitude
        for tweet in tweets :
            if (tweet.position.latitude<minLat) : minLat=tweet.position.latitude
            elif (tweet.position.latitude>maxLat) : maxLat=tweet.position.latitude
            if (tweet.position.longitude<minLon) : minLon=tweet.position.longitude
            elif (tweet.position.longitude>maxLon) : maxLon=tweet.position.longitude
            if (tweet.time<minTime) : minTime=tweet.time
            if (tweet.time>maxTime) : maxTime=tweet.time
		# on definit un carré pour localiser les tweets en calculant leftUpperCorner et rightLowerCorner
		# maxDistance est la distance euclidienne entre leftUpperCorner et rightLowerCorner
		# on definit scalesMaxDistances comme un vecteur contenant une echelle de distance entre minDistance et maxDistance
		# pour calculer temporalSeriesSize, on met 2 à la puissance (le log du nbr de paquets de secondes de timeResolution)
		# haarTransformeSize contient le minimum entre temporalSeriesSize et 2^scaleNumber
		# maximalSupportableScale est le minimum entre scaleNumber et le log de haarTransformeSize
		# totalArea permet de determiner la surface totale de traitement des tweets
        minDistance=distanceResolution
        leftUpperCorner =Position(minLat+deltaDlat/2,minLon+deltaDlon/2)
        rightLowerCorner=Position(int(maxLat/deltaDlat)*deltaDlat+deltaDlat/2,int(maxLon/deltaDlon)*deltaDlon+deltaDlon/2)
        maxDistance=leftUpperCorner.approxDistance(rightLowerCorner)
        scalesMaxDistances=getScalesMaxDistances(minDistance,maxDistance,scaleNumber)
        temporalSeriesSize=int(2**math.ceil(math.log(int((maxTime-minTime).total_seconds()/timeResolution)+1,2)))
        haarTransformeSize=min(pow(2,scaleNumber),temporalSeriesSize)
        maximalSupportableScale=min(scaleNumber,int(math.log(haarTransformeSize,2)))
        totalArea=(maxLat-minLat)*(maxLon-minLon)*DEG_LATITUDE_IN_METER*DEG_LATITUDE_IN_METER

        print "\t\tPass 2 - Construct TFVectors, IDFVector, tweetsPerTermMap, timeSerieMap and cellOfTweet"
        #Pass 2 - Construct TFVectors, IDFVector, tweetsPerTermMap, timeSerieMap and cellOfTweet
		# TFIDFVectors -> stocke 1 TFVectors pour chaque tweet 
		# TFVectors -> l'ensemble des termes presents ainsi que leur fréquence d'apparition relative a 1 tweet
		# IDFVector -> stocke pour chaque terme le nbr d'occurence
		# TweetPerTermMap -> stocke pour chaque terme, l'ensemble des tweets qui contenait ce terme
		# timeSerieMap -> contient pour chaque terme, pour chaque "cell", les heures des tweets qui contiennent ce terme avec un tel cell
		# cellOfTweet -> tableau contenant toutes les "distances cell" entre chaque tweet et (minLat,minLon) 
        TFIDFVectors=[]
        IDFVector={}
        tweetsPerTermMap={}
        timeSerieMap={}
        haarSerieMap={}
        cellOfTweet=[]
        tweetIndex=0
        for tweet in tweets :
			# cell est "la distance entre (minLat,minLon) et le tweet de traitement "
            TFVector={}
            text=tweet.text
            cell=(int((tweet.position.latitude-minLat)/deltaDlat),int((tweet.position.longitude-minLon)/deltaDlon))
            cellOfTweet.append(cell)
            timeIndex=int((tweet.time-minTime).total_seconds()/timeResolution)
            
            #Prepare the text
            text = text.lower()
            text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',text)
            text = re.sub('@[^\s]+','',text)
            text = re.sub('[\s]+', ' ', text)
            text = text.strip('\'"')
            regex="|".join(DELIMITERS)
            terms=re.split(regex,text)

            #Construct the Occurence vector
            for term in terms :
                if (TERM_MINIMAL_SIZE<len(term)<TERM_MAXIMAL_SIZE) :
                    try: TFVector[term] += 1
                    except KeyError: TFVector[term] = 1

            #Finalize the TF vector while constructing the IDF vector, tweetsPerTermMap and the timeSerieMap
			# on ajoute dans timeSerieMap, pour chaque terme, pour chaque cell, les heures des tweets qui contiennent ce terme avec un tel cell
            for term,occurence in TFVector.iteritems() :
                if term in IDFVector :
                    IDFVector[term] += 1
                    tweetsPerTermMap[term].add(tweetIndex)
                    if cell in timeSerieMap[term] :
                        try : timeSerieMap[term][cell][timeIndex]+=occurence
                        except KeyError : timeSerieMap[term][cell][timeIndex]=occurence
                    else : timeSerieMap[term][cell]={timeIndex:occurence}     
                else :
                    IDFVector[term] = 1
                    tweetsPerTermMap[term] = set([tweetIndex])
                    timeSerieMap[term]={cell:{timeIndex:occurence}}
                TFVector[term]/=floatNumberOfTweets

            TFIDFVectors.append(TFVector)
            tweetIndex+=1

        #Pass 1 on terms - Finalize IDFVectors and transform timeSerieMap to haarSerieMap of series
        #haarSerieMap = {term : {cell : [haarTransform,[sum for each timescale],[std for each time scale]], ...}, ...}
        print "\t\tPass 1 on terms - Finalize IDFVectors and transform timeSerieMap to FinestHaarTransform of series"
        TERM_INDEX=0
        SHOW_RATE=100
        print "\t\t\tNumber of terms :",len(IDFVector)
        for term,numberOfTweetOfThisTerm in IDFVector.iteritems() :
            if (TERM_INDEX%SHOW_RATE==0) : print "\t\t\t",TERM_INDEX
            TERM_INDEX+=1

            #---------------------------------------------------------------------
            #    Delete noisy terms
            #---------------------------------------------------------------------
            termToDelete=False

            #Eliminate term that appear less than minimalTermPerTweet
            if (numberOfTweetOfThisTerm<minimalTermPerTweet) : termToDelete=True

            #Eliminate terms that have poisson distribution in space
            elif (remove_noise_with_poisson_Law) :
                tweetsOfTerm=list(tweetsPerTermMap[term])
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
                tweetsOfTerm=tweetsPerTermMap[term]
                for i in tweetsOfTerm :
                    TFIDFVectorI=TFIDFVectors[i]
                    del TFIDFVectorI[term]
                del tweetsPerTermMap[term]
                del timeSerieMap[term]
                continue

            #---------------------------------------------------------------------
            #    End of noise deletion
            #---------------------------------------------------------------------
			
			#
			# on remplace dans IDFVector pour le terme que l'on traite par le log du nombre de tweets divisé par le nombre de termes total
			# on recupere dans timeSerieMap pour le terme que l'on traite, chaque cell et les tweets associés a chaque cell
            IDFVector[term]=math.log(floatNumberOfTweets/IDFVector[term],10)
            for cell, timeSerie in timeSerieMap[term].iteritems() :
                #the sum list and std list begin from 0 to scaleNumber-1 but refer to temporalScale from 1 to scaleNumber
                haarTransform,listOfSum,listOfStd=getFinestHaarTransform(timeSerie,temporalSeriesSize,scaleNumber),[0]*scaleNumber,[0]*scaleNumber

                #deleting the timeSerie 1
                timeSerie.clear()
                
				# -------------------------------------------- on remplit listOfSum et listOfStd --------------------------------------------
				# on met dans listOfSum une somme de haarTransform et dans listOfStd une somme de puissance de 2 a partir de haarTransform
                for i in range(0,2) :
                    listOfSum[0]+=haarTransform[i]
                    listOfStd[0]+=math.pow(haarTransform[i],2)
                currentScale=1
                while currentScale<maximalSupportableScale :
                    listOfSum[currentScale]+=listOfSum[currentScale-1]
                    listOfStd[currentScale]+=listOfStd[currentScale-1]
                    for i in range(int(math.pow(2,currentScale)),int(math.pow(2,currentScale+1))) :
                        listOfSum[currentScale]+=haarTransform[i]
                        listOfStd[currentScale]+=math.pow(haarTransform[i],2)
                    currentScale+=1

                for currentScale in range(0,maximalSupportableScale) :
                    listOfStd[currentScale]=math.sqrt(math.pow(2,currentScale+1)*listOfStd[currentScale]-math.pow(listOfSum[currentScale],2))
                while currentScale<scaleNumber:
                    listOfSum[currentScale]=listOfSum[maximalSupportableScale-1]
                    listOfStd[currentScale]=listOfStd[maximalSupportableScale-1]
                    currentScale+=1

				# on remplit la map
                if (cell in haarSerieMap) : haarSerieMap[cell][term]=[haarTransform,listOfSum,listOfStd]
                else : haarSerieMap[cell]={term:[haarTransform,listOfSum,listOfStd]}

            #deleting term from timeSerieMap
            timeSerieMap[term].clear()
            del timeSerieMap[term]
            
        print "\t\tPass 3 - Finalize TF-IDF Vectors" 
        #Pass 3 - Finalize TF-IDF Vectors
		# on parcourt tous les TFIDFVector pour normaliser les valeurs des termes
        for TFIDFVector in TFIDFVectors :
            TFIDFVectorNorm=0
            for term in TFIDFVector :
                TFIDFVector[term]*=IDFVector[term]
                TFIDFVectorNorm+=math.pow(TFIDFVector[term],2)
            TFIDFVectorNorm=math.sqrt(TFIDFVectorNorm)
            for term in TFIDFVector : TFIDFVector[term]/=TFIDFVectorNorm

        #delete IDFVector
        IDFVector.clear()
        
        #Done with preparation : TFIDFVectors, tweetsPerTermMap, haarSerieMap
        #Now is the time to construct the similarity matrix
        print "\t\tConstructing Similarity Matrix ..."
        SHOW_RATE=10
		# on recupere chaque tweet de l'ensemble de tweet, on construit ensuite sa liste de voisins comme les tweets ayant au moins un term en commun
		# on ne traite pas les tweets antétieurs à celui que l'on traite pour eviter les doublons
		# on recupere les mots en commun en le tweet I et J
        for i in range(numberOfTweets) :
            tweetI,TFIDFVectorI,cellI=tweets[i],TFIDFVectors[i],cellOfTweet[i]
            if (not TFIDFVectorI) : continue
            if (i%SHOW_RATE==0) : print "\t\t\t",i,";",
            TFIDFVectorIKeySet=set(TFIDFVectorI)
            cellIHaarSerieByTerm=haarSerieMap[cellI]
            positionI=tweetI.position
            if (i%SHOW_RATE==0) :print "terms :",len(TFIDFVectorIKeySet),";",

            neighboors=set()

            #Recuperation des voisins par mots (les tweets ayant au moins un term en commun)
            for term in TFIDFVectorIKeySet : neighboors|=tweetsPerTermMap[term]

            if (i%SHOW_RATE==0) : print "neighboors :",len(neighboors),"."
            for j in neighboors :
                #Ignorer les tweets qui ne sont pas apres le tweetI
                if (j<=i) : continue
                tweetJ,TFIDFVectorJ,cellJ=tweets[j],TFIDFVectors[j],cellOfTweet[j]
                if (not TFIDFVectorJ) : continue
                TFIDFVectorJKeySet=set(TFIDFVectorJ)
                cellJHaarSerieByTerm=haarSerieMap[cellJ]
                positionJ=tweetJ.position

                keysIntersection=TFIDFVectorIKeySet & TFIDFVectorJKeySet
                #---------------------------------------------------------------------------
                #  Calculate TF IDF similarity and SST Similarity
                #---------------------------------------------------------------------------
                    
                STFIDF=0
                SST=None

                spatialScale=scaleNumber
                distanceBetweetTweets=positionI.approxDistance(positionJ)
                while (spatialScale>1 and distanceBetweetTweets>scalesMaxDistances[scaleNumber-spatialScale]) : spatialScale-=1
                temporalScale=scaleNumber+1-spatialScale
                    
				# on cherche a maximiser SST comme la plus grande correlation
                for term in keysIntersection :
                    STFIDF+=TFIDFVectorI[term]*TFIDFVectorJ[term]
                    correlation=DWTBasedCorrelation(cellIHaarSerieByTerm[term],cellJHaarSerieByTerm[term],temporalScale)
                    if (SST<correlation) : SST=correlation

                #---------------------------------------------------------------------------
                #  Calculate the similarity
				# et on definit comme similarite entre I et J, la somme des produits des frequences normalisées des termes en commun entre I et J
				# multiplie par SST
                #---------------------------------------------------------------------------
                calculatedSim=SST*STFIDF
                if (calculatedSim>0 and calculatedSim>=minSimilarity) : M[i,j]=SST*STFIDF
                    
        return coo_matrix(M)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#    Basic function to get the different scale of distance between minDistance anb maxDistance
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
def getScalesMaxDistances(minDistance,maxDistance,scaleNumber) :
    alpha=(maxDistance/minDistance)**(1./(scaleNumber-1))
    scalesMaxDistances=[]
    x=minDistance
    for i in range(scaleNumber) :
        scalesMaxDistances.append(x)
        x*=alpha
    return scalesMaxDistances
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#   Haar Transformation
#	timeSerieOfTermAndCell = tableau de tweets ayant le meme cell pour un meme terme
# 	temporalSeriesSize = entier qui definit la taille du temps
# 	scaleNumber = taille de l'echelle
#	on retourne la compression par ondelettes, la transformée de Haar 
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
def getFinestHaarTransform(timeSerieOfTermAndCell,temporalSeriesSize,scaleNumber) :
	# on crée deux tableau a la bonne taille de la serie temporelle
    haarTransform=[0]*temporalSeriesSize
    timeSeriesList=[0]*temporalSeriesSize
    size=temporalSeriesSize
	# on recopie timeSerieOfTermAndCell dans timeSeriesList
    for key in timeSerieOfTermAndCell : timeSeriesList[key]=timeSerieOfTermAndCell[key]
	# on parcourt tant que on le peut
	# de 0 à size-1
	#
    while ( size>1) :
        size=size/2
        for i in range(size) :
            haarTransform[i]=float((timeSeriesList[2*i]+timeSeriesList[2*i+1]))/2
            haarTransform[i+size]=float((timeSeriesList[2*i]-timeSeriesList[2*i+1]))/2
        timeSeriesList=haarTransform[:]
    return haarTransform[0:min(pow(2,scaleNumber),temporalSeriesSize)]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#    DTW Correlation (for SST)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# si listOfStd1 = listOfStd2 : la correlation est directe on renvoie 1
# insersement si il y a anti-correlation on renvoie 0
# sinon on renvoie une valeur proche d'un calcul de la vraie correlation
#
def DWTBasedCorrelation(finestHaarTransform_1,finestHaarTransform_2,temporalScale) :
    std1=finestHaarTransform_1[2][temporalScale-1]
    std2=finestHaarTransform_2[2][temporalScale-1]
    if (std1==std2==0) : return 1
    if (std1*std2==0) : return 0
    sum1=finestHaarTransform_1[1][temporalScale-1]
    sum2=finestHaarTransform_2[1][temporalScale-1]
	# haarTransform = finestHaarTransform_1[0]
    maxSize=min(pow(2,temporalScale),len(finestHaarTransform_1[0]))
    prodSum=0
	# on somme les produits 2 a 2 des haarTransform des 2 tweets
    for v1,v2 in zip(finestHaarTransform_1[0][0:maxSize],finestHaarTransform_2[0][0:maxSize]) : prodSum+=v1*v2
    return (maxSize*prodSum-sum1*sum2)/(std1*std2)
