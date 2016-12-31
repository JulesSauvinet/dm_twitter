import sys, subprocess, math, re, numpy as np
from sklearn.neighbors import NearestNeighbors
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from ...model.Position import Position
from ...model.Event import Event
from Utils.Constants import *
import time
import os.path


class OptimisedEventDetectorMEDBased:
    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Class constructor
	# 	pour faire de la detection d'evenements
	#	il faut des tweets, un temps de resolution et une distance min de resolution, une echelle et une valeur minimale de similarite significative
    # -------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, tweets, timeResolution=1800, distanceResolution=100, scaleNumber=4, minSimilarity=0.5, distanceThreshold=10):
        """
        timeResolution : define the time resolution for time series
        distanceResolution : define a cell size in meter (not exact)
        scaleNumber : nscale in the paper
        """
        self.tweets = np.array(tweets)
        self.timeResolution = timeResolution
        self.distanceResolution = distanceResolution
        self.scaleNumber = scaleNumber
        self.minSimilarity = max(min(minSimilarity, 1), 0)
        self.events = []
        self.distanceThreshold=distanceThreshold

    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Event detection
	# pour detecter un evenement, on recupere les clusters resultant du clustering pour une date donnee
    # on recupere la liste des ID des clusters crees, methode ensembliste, une seule occurence
	# et on renvoie un ensemble, qui correspond a l'ensemble des evenements pour une date donnee
    # -------------------------------------------------------------------------------------------------------------------------------------
    def getEvents(self, date, minimalTermPerTweet=5, minimalTermPerTweetElasticity=5,remove_noise_with_poisson_Law=False,elasticity=False,geolocalisation=False):
        """
        get the list of important events
        """

        #if (self.tweets):
        if (len(self.tweets)>0):

            print "Detecting events ..."
			# pour detecter un evenement, on recupere les clusters resultant du clustering pour une date donnee
            realClusters = self.getClusters(date, minimalTermPerTweet=minimalTermPerTweet,minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
                                            remove_noise_with_poisson_Law=remove_noise_with_poisson_Law,elasticity=elasticity,geolocalisation=geolocalisation)
											
            # on recupere dans clustersUniqueId, la liste des ID des clusters crees, methode ensembliste, une seule occurence
			# on recupere chaque id de cluster, 
			#	on met dans tweetsOfClusterId, tous les tweets qui appartiennent a l'id du cluster que l'on traite
			#	on definit comme evenement l'ensemble de ces tweets
			#	si notre evenement est defini comme important, on l'ajoute a l'ensemble de tous les evenements
			# on renvoie cet ensemble, qui correspond a l'ensemble des evenements pour une date donnee
            events = []
            if realClusters is not None:
                if len(realClusters > 0):
                    clustersUniqueId = set(realClusters)
                    print "\tConstructing events from clusters ..."
                    i = 0
                    #print "LEN CLUSTERID", len(clustersUniqueId)
                    #print "CLUSTERID", clustersUniqueId
                    #print "tweet len", len(self.tweets)
                    #print "realClusters", realClusters
                    #print "realClusterslen", len(realClusters)
                    for clusterId in clustersUniqueId:
                        tweetsOfClusterId = self.tweets[realClusters == clusterId]
                        event = Event(tweetsOfClusterId)
                        if (self.isEventImportant(event)): events.append(event)
            self.events = events
            return events
        else:
            print "No events detected because there is no tweets for the date : ", str(date)
            return []

    # -------------------------------------------------------------------------------------------------------------------------------------
	# si le nombre de personnes ayant tweete n'est pas assez important ou si il n'y a pas assez de tweets --> on renvoie faux
	# tweetPerUserNumber contient le nombre de tweets par utilisateur
	# maximumProportionInThisEvent contient le nombre de tweets de la personne qui a le plus tweete divise par le nbr total de tweets
	# on renvoie vrai si la proportion de tweets par personne n'est pas exageree
    # -------------------------------------------------------------------------------------------------------------------------------------
    def isEventImportant(self, event):
        """
        evaluate if yes or no the event is important
        """
        if (event.userNumber < MIN_USER_NUMBER or len(event.tweets) < MIN_TWEETS_NUMBER): return False
        tweetPerUserNumber = {}
        for tweet in self.tweets:
            try:
                tweetPerUserNumber[tweet.userId] += 1
            except KeyError:
                tweetPerUserNumber[tweet.userId] = 1
        maximumProportionInThisEvent = float(tweetPerUserNumber[max(list(tweetPerUserNumber), key=lambda userId: tweetPerUserNumber[userId])]) / len(self.tweets)
        return (maximumProportionInThisEvent < MAX_TOLERATED_PER_USER)

    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Event vizualisation
	#	Renvoie, un evenement sous forme d'une chaine de caracteres afin de l'afficher dans la console lors de l'execution
    # -------------------------------------------------------------------------------------------------------------------------------------
    def getStringOfEvent(self, event):
        NUM_DIGIT = 10 ** 2
        SEPARATOR = "\t|"
        PERCENTAGE = 0.8

        firstIndiceOfInterval, lastIndiceOfInterval = 0, int(PERCENTAGE * len(event.tweets))
        estimatedEventDuration = event.tweets[firstIndiceOfInterval].delay(event.tweets[lastIndiceOfInterval])

        while (lastIndiceOfInterval < len(event.tweets)):
            newEventDuration = event.tweets[firstIndiceOfInterval].delay(event.tweets[lastIndiceOfInterval])
            if (newEventDuration < estimatedEventDuration): estimatedEventDuration = newEventDuration
            firstIndiceOfInterval += 1
            lastIndiceOfInterval += 1

        S = "|" + SEPARATOR.join([str(event.eventMedianTime),
                                  str(int(estimatedEventDuration)),
                                  str(float(int(NUM_DIGIT * event.eventCenter.latitude)) / NUM_DIGIT),
                                  str(float(int(NUM_DIGIT * event.eventCenter.longitude)) / NUM_DIGIT),
                                  str(float(int(NUM_DIGIT * event.eventRadius)) / NUM_DIGIT),
                                  str(event.userNumber),
                                  str(len(event.tweets)),
                                  ",".join(event.importantHashtags)]) + SEPARATOR
        return S
		
    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Fonction pour recuperer les meilleurs evenements
	#	affichage sous forme de tableau du resultat
	#	on trie tous les evenements par ordre decroissant, en ne gardant que les "top" premiers, top passe en parametre
    # -------------------------------------------------------------------------------------------------------------------------------------
    def showTopEvents(self, top=10):
        if not self.events:
            "No events detected !"
            return

        SIZE_OF_LINE = 40
        SEPARATOR = "\t|"
        HEADER = "|" + SEPARATOR.join(
            ["Median time", "estimated duration (s)", "mean latitude", "mean longitude", "radius (m)", "user number",
             "tweets number", "top hashtags"]) + SEPARATOR

        TopEvents = sorted(self.events, key=lambda event: len(event.tweets), reverse=True)[
                    0:min(max(1, top), len(self.events))]

        print "-" * SIZE_OF_LINE
        print HEADER
        print "-" * SIZE_OF_LINE
        for event in TopEvents:
            print self.getStringOfEvent(event)
            print "-" * SIZE_OF_LINE

    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Clustering and Similarity matrix construction
	#	on construit un fichier d'entree et un fichier de sortie propre a la date d'entree
	#	le fichier d'entree contient la matrice de similarite, sur une meme ligne on a un tweet i et un tweet j puis la valeur de leur similarite
	#	le fichier de sortie contenant la matrice de correspondance est parse puis renvoye sous forme de tableau
    # -------------------------------------------------------------------------------------------------------------------------------------
    def getClusters(self, date ,minimalTermPerTweet=5, minimalTermPerTweetElasticity=5, remove_noise_with_poisson_Law=False,elasticity=False,geolocalisation=False):
        """
        This method use ModularityOptimizer.jar
        """
        realClusters = []
        weightsFilePath = "input"+date+".txt"
        clusterFilePath = "output"+date+".txt"

        # Creating the input file
		# on construit la matrice de similarite, et on met les donnees resultats dans le fichier d'entree
        print "\tBuilding similarity matrix ..."
        self.build(minimalTermPerTweet=minimalTermPerTweet, minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
				   remove_noise_with_poisson_Law=remove_noise_with_poisson_Law, similarityFilePath=weightsFilePath,elasticity=elasticity,geolocalisation=geolocalisation)

		# on construit mtn le fichier de sortie qui associe a chaque tweet le numero de clusters auquel il appartient
		#
        if os.path.isfile(weightsFilePath):
            fic = open(weightsFilePath, 'r')
            read = fic.readlines()
            nblines = len(read)
            fic.close()
            if nblines > 1:
                # Creating the output file (command execution)
					#inputFileName = weightsFilePath
					#outputFileName = clusterFilePath
					#modularityFunction = 1 : standard
					#resolution = 0.5
					#algorithm = 2 : Louvain with multilevel refinement
					#nRandomStarts = 10
					#nIterations = 10
					#randomSeed = 0
					#printOutput = 0 
                print "\tClustering ..."
                command = "java -jar eventDetectionFromTwitter/ModularityOptimizer.jar {0} {1} 1 0.5 2 10 10 0 0".format(weightsFilePath, clusterFilePath)
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                process.wait()

                # Get The events
				# on recupere les donnees du fichier de sortie contenant la matrice de correspondance
				# on met dans realClusters, pour chaque ligne, le cluster auquel il appartient
                print "\tReading clusters from a file ..."
                if os.path.exists(clusterFilePath) :
                    with open(clusterFilePath) as f:
                        realClusters = map(int, f.readlines())
        return np.array(realClusters)

		
	# construit la meme matrice que MED, juste que au lieu de renvoyer une matrice au sens propre du terme, on ecrit dans un fichier
    def build(self, minimalTermPerTweet=5, minimalTermPerTweetElasticity=1, remove_noise_with_poisson_Law=False, similarityFilePath="input.txt",elasticity=False,geolocalisation=False):
        """
        Return an upper sparse triangular matrix of similarity j>i
        """
		# on recupere le temps, la resolution temporale, la resolution de distance, une echelle, les tweets et le pourcentage de similarite
        staringTime = time.time()
        timeResolution = self.timeResolution
        distanceResolution = self.distanceResolution
        scaleNumber = self.scaleNumber
        tweets = self.tweets
        minSimilarity = self.minSimilarity

        numberOfTweets = len(tweets)		
        floatNumberOfTweets = float(numberOfTweets)
        deltaDlat = float(distanceResolution) / DEG_LATITUDE_IN_METER
        deltaDlon = float(distanceResolution) / DEG_LATITUDE_IN_METER
        print "\t\tPass 1 - Get General Information"
        # Pass 1 - Get General Information
		# on va recuperer la date de debut et la date de fin des tweets, ainsi que la latitude et longitude min et max des tweets
        minTime = maxTime = tweets[0].time
        minLat = maxLat = float(tweets[0].position.latitude)
        minLon = maxLon = float(tweets[0].position.longitude)
        for tweet in tweets:
            if (float(tweet.position.latitude < minLat)):
                minLat = float(tweet.position.latitude)
            elif (float(tweet.position.latitude > maxLat)):
                maxLat = float(tweet.position.latitude)
            if (float(tweet.position.longitude) < minLon):
                minLon = float(tweet.position.longitude)
            elif (float(tweet.position.longitude) > maxLon):
                maxLon = float(tweet.position.longitude)
            if (tweet.time < minTime): minTime = tweet.time
            if (tweet.time > maxTime): maxTime = tweet.time
		# on definit un carre pour localiser les tweets en calculant leftUpperCorner et rightLowerCorner
		# minDistance est egale a la distance de resolution donnee au debut
		# leftUpperCorner definit le coin en haut a gauche grace au valeurs minimales calculees
		# x est la latitude maximale
		# y est la longitude maximale
		# rightLowerCorner definit le coin en bas a droite grace au valeurs maximales calculees x et y
		# maxDistance est la distance euclidienne entre leftUpperCorner et rightLowerCorner
		# on definit scalesMaxDistances comme un vecteur contenant une echelle de taille scaleNumber de distance entre minDistance et maxDistance
		# pour calculer temporalSeriesSize, on met 2 a la puissance (le log du nbr de paquets de secondes de timeResolution)
		# haarTransformeSize contient le minimum entre temporalSeriesSize et 2^scaleNumber
		# maximalSupportableScale est le minimum entre scaleNumber et le log en base 2 de haarTransformeSize
		# totalArea permet de determiner la surface totale de traitement des tweets
        minDistance = distanceResolution
        leftUpperCorner = Position(float(minLat) + float(deltaDlat) / 2, float(minLon) + float(deltaDlon) / 2)
        x = int(float(maxLat) / float(deltaDlat)) * float(deltaDlat) + float(deltaDlat) / 2
        y = int(float(maxLon) / deltaDlon) * deltaDlon + deltaDlon / 2
        rightLowerCorner = Position(x, y)
        maxDistance = leftUpperCorner.approxDistance(rightLowerCorner)
        scalesMaxDistances = getScalesMaxDistances(minDistance, maxDistance, scaleNumber)
        temporalSeriesSize = int(
            2 ** math.ceil(math.log(int((maxTime - minTime).total_seconds() / timeResolution) + 1, 2)))
        haarTransformeSize = min(pow(2, scaleNumber), temporalSeriesSize)
        maximalSupportableScale = min(scaleNumber, int(math.log(haarTransformeSize, 2)))
        totalArea = (float(maxLat) - float(minLat)) * (
        float(maxLon) - float(minLon)) * DEG_LATITUDE_IN_METER * DEG_LATITUDE_IN_METER

        print "\t\tPass 2 - Construct TFVectors, IDFVector, tweetsPerTermMap, timeSerieMap and cellOfTweet"
        # Pass 2 - Construct TFVectors, IDFVector, tweetsPerTermMap, timeSerieMap and cellOfTweet
		# TFIDFVectors -> stocke 1 TFVectors pour chaque tweet 
		# TFVector -> l'ensemble des termes presents ainsi que leur frequence d'apparition relative a 1 tweet
		# IDFVector -> stocke pour chaque terme le nbr d'occurence
		# tweetsPerTermMap -> stocke pour chaque terme, l'ensemble des tweets qui contenait ce terme
		# timeSerieMap -> contient pour chaque terme, pour chaque "cell", les heures des tweets qui contiennent ce terme avec un tel cell
		# cellOfTweet -> tableau contenant toutes les "distances cell" entre chaque tweet et (minLat,minLon) 
        TFIDFVectors = []
        IDFVector = {}
        tweetsPerTermMap = {}
        timeSerieMap = {}
        haarSerieMap = {}
        cellOfTweet = []
        tweetIndex = 0
        for tweet in tweets:
            TFVector = {}
            text = tweet.text
            cell = (int((float(tweet.position.latitude) - minLat) / deltaDlat),
                    int((float(tweet.position.longitude) - minLon) / deltaDlon))
            cellOfTweet.append(cell)
            timeIndex = int((tweet.time - minTime).total_seconds() / timeResolution)

            # Prepare the text
            text = text.lower()
            text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', text)
            text = re.sub('@[^\s]+', '', text)
            text = re.sub('[\s]+', ' ', text)
            text = text.strip('\'"')
            regex = "|".join(DELIMITERS)
            terms = re.split(regex, text)

            # Construct the Occurence vector
            for term in terms:
                if (TERM_MINIMAL_SIZE < len(term) < TERM_MAXIMAL_SIZE):
                    try:
                        TFVector[term] += 1
                    except KeyError:
                        TFVector[term] = 1

            # Finalize the TF vector while constructing the IDF vector, tweetsPerTermMap and the timeSerieMap
			# on ajoute dans timeSerieMap, pour chaque terme, pour chaque cell, les heures des tweets qui contiennent ce terme avec un tel cell
            for term, occurence in TFVector.iteritems():
                if term in IDFVector:
                    IDFVector[term] += 1
                    tweetsPerTermMap[term].add(tweetIndex)
                    if cell in timeSerieMap[term]:
                        try:
                            timeSerieMap[term][cell][timeIndex] += occurence
                        except KeyError:
                            timeSerieMap[term][cell][timeIndex] = occurence
                    else:
                        timeSerieMap[term][cell] = {timeIndex: occurence}
                else:
                    IDFVector[term] = 1
                    tweetsPerTermMap[term] = set([tweetIndex])
                    timeSerieMap[term] = {cell: {timeIndex: occurence}}
                TFVector[term] /= floatNumberOfTweets

            TFIDFVectors.append(TFVector)
            tweetIndex += 1

        # Pass 1 on terms - Finalize IDFVectors and transform timeSerieMap to haarSerieMap of series
        # haarSerieMap = {term : {cell : [haarTransform,[sum for each timescale],[std for each time scale]], ...}, ...}
        print "\t\tPass 1 on terms - Finalize IDFVectors and transform timeSerieMap to FinestHaarTransform of series"
        TERM_INDEX = 0
        SHOW_RATE = 100
        print "\t\t\tNumber of terms :", len(IDFVector)
			
        for term, numberOfTweetOfThisTerm in IDFVector.iteritems():
            # if (TERM_INDEX%SHOW_RATE==0) : print "\t\t\t",TERM_INDEX
            if (10 <= numberOfTweetOfThisTerm <= 15): print term.encode("utf-8"), numberOfTweetOfThisTerm
            TERM_INDEX += 1

            # ---------------------------------------------------------------------
            #    Delete noisy terms
            # ---------------------------------------------------------------------
            termToDelete = False
            tweetsOfTerm = list(tweetsPerTermMap[term])

            # Eliminate term that appear less than minimalTermPerTweet
            if (elasticity == False and numberOfTweetOfThisTerm < minimalTermPerTweet) :
                termToDelete = True
            elif (elasticity == True and numberOfTweetOfThisTerm < int(minimalTermPerTweetElasticity*numberOfTweets)) :
                termToDelete = True
            # Eliminate terms that have poisson distribution in space
            elif (remove_noise_with_poisson_Law):
				numberOfTweetsPerThres = [0] * len(S_FOR_FILTERING)
				for indiceI in range(numberOfTweetOfThisTerm):
					tweetI = tweets[tweetsOfTerm[indiceI]]
					positionI = tweetI.position
					for indiceJ in range(indiceI + 1, numberOfTweetOfThisTerm):
						tweetJ = tweets[tweetsOfTerm[indiceJ]]
						positionJ = tweetJ.position
						k = len(S_FOR_FILTERING) - 1
						distanceIJ = positionI.approxDistance(positionJ)
						while (k >= 0 and distanceIJ <= S_FOR_FILTERING[k]):
							numberOfTweetsPerThres[k] += 1
							k -= 1
				LValuesPerThres = [
					math.sqrt(((2 * totalArea * numPerThres) / numberOfTweetOfThisTerm) / math.pi) - thres for
					thres, numPerThres in zip(S_FOR_FILTERING, numberOfTweetsPerThres)]
				meanLValue = sum(LValuesPerThres) / len(LValuesPerThres)
				if (meanLValue < THRESHOLD_FOR_FILTERING): termToDelete = True

            # Delete term
            if (termToDelete):
                tweetsOfTerm = tweetsPerTermMap[term]
                for i in tweetsOfTerm:
                    TFIDFVectorI = TFIDFVectors[i]
                    del TFIDFVectorI[term]
                del tweetsPerTermMap[term]
                del timeSerieMap[term]
                continue

            # ---------------------------------------------------------------------
            #    End of noise deletion
            # ---------------------------------------------------------------------
			
			#
			# on remplace dans IDFVector pour le terme que l'on traite par le log du nombre de tweets divise par le nombre de termes total
			# on recupere dans timeSerieMap pour le terme que l'on traite, chaque cell et les tweets associes a chaque cell
            IDFVector[term] = math.log(floatNumberOfTweets / IDFVector[term], 10)
            for cell, timeSerie in timeSerieMap[term].iteritems():
                # the sum list and std list begin from 0 to scaleNumber-1 but refer to temporalScale from 1 to scaleNumber
                haarTransform, listOfSum, listOfStd = getFinestHaarTransform(timeSerie, temporalSeriesSize,scaleNumber), [0] * scaleNumber, [0] * scaleNumber

                # deleting the timeSerie 1
                timeSerie.clear()
                
				# -------------------------------------------- on remplit listOfSum et listOfStd --------------------------------------------
				# on met dans listOfSum une somme de haarTransform et dans listOfStd une somme de puissance de 2 a partir de haarTransform
                if len(haarTransform) < 2:
                    return;
                else :
                    for i in range(0, 2):
                        listOfSum[0] += haarTransform[i]
                        listOfStd[0] += math.pow(haarTransform[i], 2)
                    currentScale = 1
                    while currentScale < maximalSupportableScale:
                        listOfSum[currentScale] += listOfSum[currentScale - 1]
                        listOfStd[currentScale] += listOfStd[currentScale - 1]
                        for i in range(int(math.pow(2, currentScale)), int(math.pow(2, currentScale + 1))):
                            listOfSum[currentScale] += haarTransform[i]
                            listOfStd[currentScale] += math.pow(haarTransform[i], 2)
                        currentScale += 1

                    for currentScale in range(0, maximalSupportableScale):
                        listOfStd[currentScale] = math.sqrt(
                            math.pow(2, currentScale + 1) * listOfStd[currentScale] - math.pow(listOfSum[currentScale], 2))
                    while currentScale < scaleNumber:
                        listOfSum[currentScale] = listOfSum[maximalSupportableScale - 1]
                        listOfStd[currentScale] = listOfStd[maximalSupportableScale - 1]
                        currentScale += 1

                    if (cell in haarSerieMap):
                        haarSerieMap[cell][term] = [haarTransform, listOfSum, listOfStd]
                    else:
                        haarSerieMap[cell] = {term: [haarTransform, listOfSum, listOfStd]}

            # deleting term from timeSerieMap
            timeSerieMap[term].clear()
            del timeSerieMap[term]

        print "\t\tPass 3 - Finalize TF-IDF Vectors"
        # Pass 3 - Finalize TF-IDF Vectors
		# on parcourt tous les TFIDFVector pour normaliser les valeurs des termes
        for TFIDFVector in TFIDFVectors:
            TFIDFVectorNorm = 0
            for term in TFIDFVector:
                TFIDFVector[term] *= IDFVector[term]
                TFIDFVectorNorm += math.pow(TFIDFVector[term], 2)
            TFIDFVectorNorm = math.sqrt(TFIDFVectorNorm)
            for term in TFIDFVector: TFIDFVector[term] /= TFIDFVectorNorm

        # delete IDFVector
        IDFVector.clear()

        elapsed_time = (time.time() - staringTime)
        print "-" * 40
        print "Elapsed time : {0}s".format(elapsed_time)
        print "-" * 40
        # Done with preparation : TFIDFVectors, tweetsPerTermMap, haarSerieMap
        # Now is the time to construct the similarity matrix
        print "\t\tConstructing Similarity Matrix ..."
        SHOW_RATE = 10
		# on recupere chaque tweet de l'ensemble de tweet, on construit ensuite sa liste de voisins comme les tweets ayant au moins un term en commun
		# on ne traite pas les tweets antetieurs a celui que l'on traite pour eviter les doublons
		# on recupere les mots en commun en le tweet I et J

        similarityFile = open(similarityFilePath, 'w')
        lastvisted = 0
        distanceThreshold=float(self.distanceThreshold)
        distanceThresholdInDegree=distanceThreshold/DEG_LATITUDE_IN_METER
        spatialIndex=NearestNeighbors(radius=distanceThresholdInDegree, algorithm='auto')
        spatialIndex.fit(np.array([(tweet.position.latitude,tweet.position.longitude) for tweet in tweets]))
		
        for i in range(numberOfTweets):
            tweetI, TFIDFVectorI, cellI = tweets[i], TFIDFVectors[i], cellOfTweet[i]
            if (not TFIDFVectorI): continue
            if (i % SHOW_RATE == 0): print "\t\t\t", i, ";",
            TFIDFVectorIKeySet = set(TFIDFVectorI)
            cellIHaarSerieByTerm = haarSerieMap[cellI]
            positionI = tweetI.position
            if (i % SHOW_RATE == 0): print "terms :", len(TFIDFVectorIKeySet), ";",

            neighboors = set()

            # Recuperation des voisins par mots (les tweets ayant au moins un term en commun)
			# on mettra ici, si geolocalisation=True, l'appel de :
			# spatialIndex=NearestNeighbors(radius=distanceThresholdInDegree, algorithm='auto')
			# spatialIndex.fit(np.array([(tweet.position.latitude,tweet.position.longitude) for tweet in tweets]))
            if(not geolocalisation) :
                for term in TFIDFVectorIKeySet: neighboors |= tweetsPerTermMap[term]
            else :
                position=np.array([tweetI.position.latitude,tweetI.position.longitude]).reshape(-1,2)
                neighboors&=set(spatialIndex.radius_neighbors(position)[1][0])

            if (i % SHOW_RATE == 0): print "neighboors :", len(neighboors), "."
            for j in neighboors:
                # Ignorer les tweets qui ne sont pas apres le tweetI
                if (j <= i): continue
                tweetJ, TFIDFVectorJ, cellJ = tweets[j], TFIDFVectors[j], cellOfTweet[j]
                if (not TFIDFVectorJ): continue
                TFIDFVectorJKeySet = set(TFIDFVectorJ)
                cellJHaarSerieByTerm = haarSerieMap[cellJ]
                positionJ = tweetJ.position

                keysIntersection = TFIDFVectorIKeySet & TFIDFVectorJKeySet
                # ---------------------------------------------------------------------------
                #  Calculate TF IDF similarity and SST Similarity
                # ---------------------------------------------------------------------------

                STFIDF = 0
                SST = None

                spatialScale = scaleNumber
                distanceBetweetTweets = positionI.approxDistance(positionJ)
                while (spatialScale > 1 and distanceBetweetTweets > scalesMaxDistances[
                        scaleNumber - spatialScale]): spatialScale -= 1
                temporalScale = scaleNumber + 1 - spatialScale
                    
				# on cherche a maximiser SST comme la plus grande correlation
                for term in keysIntersection:
                    STFIDF += TFIDFVectorI[term] * TFIDFVectorJ[term]
                    correlation = DWTBasedCorrelation(cellIHaarSerieByTerm[term], cellJHaarSerieByTerm[term],
                                                      temporalScale)
                    if (SST < correlation): SST = correlation

                # ---------------------------------------------------------------------------
                #  Calculate the similarity
				#  si SST > 0 -> si on n'est pas anti-correle
				#  et on definit comme similarite entre I et J, la somme des produits des frequences normalisees des termes en commun entre I et J
				#  multiplie par SST
				#  on ecrit dans le fichier le numero du cluster i le numero du cluster j et la valeur de similarite
				#  lastvisted permet de savoir si on a traite tous les clusters
                # ---------------------------------------------------------------------------
                if (SST > 0):
                    if (j > lastvisted): lastvisted = j
                    calculatedSim = SST * STFIDF
                    if (calculatedSim > 0 and calculatedSim >= minSimilarity): 
						similarityFile.write("{0}\t{1}\t{2}\n".format(i, j, SST * STFIDF))
        if (lastvisted < numberOfTweets - 1): similarityFile.write(
            "{0}\t{1}\t{2}\n".format(numberOfTweets - 2, numberOfTweets - 1, 0))
        similarityFile.close();


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
#    Basic function to get the different scale of distance between minDistance anb maxDistance
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def getScalesMaxDistances(minDistance, maxDistance, scaleNumber):
    alpha = (maxDistance / minDistance) ** (1. / (scaleNumber - 1))
    scalesMaxDistances = []
    x = minDistance
    for i in range(scaleNumber):
        scalesMaxDistances.append(x)
        x *= alpha
    return scalesMaxDistances


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
#    Haar Transformation
# timeSerieOfTermAndCell = tableau de tweets ayant le meme cell pour un meme terme
# temporalSeriesSize = entier qui definit la taille du temps
# scaleNumber = taille de l'echelle
# on retourne la compression par ondelettes, la transformee de Haar 
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def getFinestHaarTransform(timeSerieOfTermAndCell, temporalSeriesSize, scaleNumber):
    haarTransform = [0] * temporalSeriesSize
    timeSeriesList = [0] * temporalSeriesSize
    size = temporalSeriesSize
	# on recopie timeSerieOfTermAndCell dans timeSeriesList
    for key in timeSerieOfTermAndCell: timeSeriesList[key] = timeSerieOfTermAndCell[key]
	# on parcourt tant que on le peut
	# de 0 a size-1
	#
    while (size > 1):
        size = size / 2
        for i in range(size):
            haarTransform[i] = float((timeSeriesList[2 * i] + timeSeriesList[2 * i + 1])) / 2
            haarTransform[i + size] = float((timeSeriesList[2 * i] - timeSeriesList[2 * i + 1])) / 2
        timeSeriesList = haarTransform[:]
    return haarTransform[0:min(pow(2, scaleNumber), temporalSeriesSize)]


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
#    DTW Correlation (for SST)
# si listOfStd1 = listOfStd2 : la correlation est directe on renvoie 1
# insersement si il y a anti-correlation on renvoie 0
# sinon on renvoie une valeur proche d'un calcul de la vraie correlation
# --------------------------------------------------------------------------------------------------------------------------------------------------------------

def DWTBasedCorrelation(finestHaarTransform_1, finestHaarTransform_2, temporalScale):
    std1 = finestHaarTransform_1[2][temporalScale - 1]
    std2 = finestHaarTransform_2[2][temporalScale - 1]
    if (std1 == std2 == 0): return 1
    if (std1 * std2 == 0): return 0
    sum1 = finestHaarTransform_1[1][temporalScale - 1]
    sum2 = finestHaarTransform_2[1][temporalScale - 1]
	# haarTransform = finestHaarTransform_1[0]
    maxSize = min(pow(2, temporalScale), len(finestHaarTransform_1[0]))
    prodSum = 0
	# on somme les produits 2 a 2 des haarTransform des 2 tweets
    for v1, v2 in zip(finestHaarTransform_1[0][0:maxSize], finestHaarTransform_2[0][0:maxSize]): prodSum += v1 * v2
    return (maxSize * prodSum - sum1 * sum2) / (std1 * std2)
