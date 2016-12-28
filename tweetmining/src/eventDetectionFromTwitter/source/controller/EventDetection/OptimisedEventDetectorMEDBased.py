import sys, subprocess, math, re, numpy as np
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from ...model.Position import Position
from ...model.Event import Event
from Utils.Constants import *
import time
import os.path


class OptimisedEventDetectorMEDBased:
    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Class constructor
    # -------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, tweets, timeResolution=1800, distanceResolution=100, scaleNumber=4, minSimilarity=0.5):
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

    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Event detection
    # -------------------------------------------------------------------------------------------------------------------------------------
    def getEvents(self, date, minimalTermPerTweet=5, minimalTermPerTweetElasticity=5,remove_noise_with_poisson_Law=False,elasticity=False):
        """
        get the list of important events
        """

        #if (self.tweets):
        if (len(self.tweets)>0):

            print "Detecting events ..."

            realClusters = self.getClusters(date, minimalTermPerTweet=minimalTermPerTweet,minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
                                            remove_noise_with_poisson_Law=remove_noise_with_poisson_Law,elasticity=False)
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
        maximumProportionInThisEvent = float(
            tweetPerUserNumber[max(list(tweetPerUserNumber), key=lambda userId: tweetPerUserNumber[userId])]) / len(
            self.tweets)
        return (maximumProportionInThisEvent < MAX_TOLERATED_PER_USER)

    # -------------------------------------------------------------------------------------------------------------------------------------
    #   Event vizualisation
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
    # -------------------------------------------------------------------------------------------------------------------------------------
    def getClusters(self, date ,minimalTermPerTweet=5, minimalTermPerTweetElasticity=5, remove_noise_with_poisson_Law=False,elasticity=False):
        """
        This method use ModularityOptimizer.jar
        """
        realClusters = []
        weightsFilePath = "input"+date+".txt"
        clusterFilePath = "output"+date+".txt"

        # Creating the input file
        print "\tBuilding similarity matrix ..."
        self.build(minimalTermPerTweet=minimalTermPerTweet, minimalTermPerTweetElasticity=minimalTermPerTweetElasticity,
				   remove_noise_with_poisson_Law=remove_noise_with_poisson_Law, similarityFilePath=weightsFilePath,elasticity=False)



        if os.path.isfile(weightsFilePath):
            fic = open(weightsFilePath, 'r')
            read = fic.readlines()
            nblines = len(read)
            fic.close()
            if nblines > 1:
                # Creating the output file (command execution)
                print "\tClustering ..."
                command = "java -jar eventDetectionFromTwitter/ModularityOptimizer.jar {0} {1} 1 0.5 2 10 10 0 0".format(
                    weightsFilePath, clusterFilePath)
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                process.wait()

                # Get The events
                print "\tReading clusters from a file ..."
                if os.path.exists(clusterFilePath) :
                    with open(clusterFilePath) as f:
                        realClusters = map(int, f.readlines())
        return np.array(realClusters)

    def build(self, minimalTermPerTweet=5, minimalTermPerTweetElasticity=5, remove_noise_with_poisson_Law=False, similarityFilePath="input.txt",elasticity=False):
        """
        Return an upper sparse triangular matrix of similarity j>i
        """
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

            # Eliminate term that appear less than minimalTermPerTweet
            if (elasticity==False) :
                if (numberOfTweetOfThisTerm < minimalTermPerTweet):
					termToDelete = True
            else :
				if ((numberOfTweetOfThisTerm < minimalTermPerTweet*numberOfTweets) or (numberOfTweetOfThisTerm < minimalTermPerTweetElasticity)):
					termToDelete = True			

            # Eliminate terms that have poisson distribution in space
				elif (remove_noise_with_poisson_Law):
					tweetsOfTerm = list(tweetsPerTermMap[term])
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

            IDFVector[term] = math.log(floatNumberOfTweets / IDFVector[term], 10)
            for cell, timeSerie in timeSerieMap[term].iteritems():
                # the sum list and std list begin from 0 to scaleNumber-1 but refer to temporalScale from 1 to scaleNumber
                haarTransform, listOfSum, listOfStd = getFinestHaarTransform(timeSerie, temporalSeriesSize,
                                                                             scaleNumber), [0] * scaleNumber, [
                                                          0] * scaleNumber

                # deleting the timeSerie 1
                timeSerie.clear()

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

        similarityFile = open(similarityFilePath, 'w')
        lastvisted = 0
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
            for term in TFIDFVectorIKeySet: neighboors |= tweetsPerTermMap[term]

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

                for term in keysIntersection:
                    STFIDF += TFIDFVectorI[term] * TFIDFVectorJ[term]
                    correlation = DWTBasedCorrelation(cellIHaarSerieByTerm[term], cellJHaarSerieByTerm[term],
                                                      temporalScale)
                    if (SST < correlation): SST = correlation

                # ---------------------------------------------------------------------------
                #  Calculate the similarity
                # ---------------------------------------------------------------------------
                if (SST > 0):
                    if (j > lastvisted): lastvisted = j
                    calculatedSim = SST * STFIDF
                    if (calculatedSim > 0 and calculatedSim >= minSimilarity): similarityFile.write(
                        "{0}\t{1}\t{2}\n".format(i, j, SST * STFIDF))
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
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def getFinestHaarTransform(timeSerieOfTermAndCell, temporalSeriesSize, scaleNumber):
    haarTransform = [0] * temporalSeriesSize
    timeSeriesList = [0] * temporalSeriesSize
    size = temporalSeriesSize
    for key in timeSerieOfTermAndCell: timeSeriesList[key] = timeSerieOfTermAndCell[key]
    while (size > 1):
        size = size / 2
        for i in range(size):
            haarTransform[i] = float((timeSeriesList[2 * i] + timeSeriesList[2 * i + 1])) / 2
            haarTransform[i + size] = float((timeSeriesList[2 * i] - timeSeriesList[2 * i + 1])) / 2
        timeSeriesList = haarTransform[:]
    return haarTransform[0:min(pow(2, scaleNumber), temporalSeriesSize)]


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
#    DTW Correlation (for SST)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def DWTBasedCorrelation(finestHaarTransform_1, finestHaarTransform_2, temporalScale):
    std1 = finestHaarTransform_1[2][temporalScale - 1]
    std2 = finestHaarTransform_2[2][temporalScale - 1]
    if (std1 == std2 == 0): return 1
    if (std1 * std2 == 0): return 0
    sum1 = finestHaarTransform_1[1][temporalScale - 1]
    sum2 = finestHaarTransform_2[1][temporalScale - 1]
    maxSize = min(pow(2, temporalScale), len(finestHaarTransform_1[0]))
    prodSum = 0
    for v1, v2 in zip(finestHaarTransform_1[0][0:maxSize], finestHaarTransform_2[0][0:maxSize]): prodSum += v1 * v2
    return (maxSize * prodSum - sum1 * sum2) / (std1 * std2)
