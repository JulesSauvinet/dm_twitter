# coding=utf-8
# Dans ce module, on definit un evenement.
# On construit un evenement a partir d'une liste de tweets que l'on tri par ordre croissant de publication
#
# On décrit un evenement par :
#	- son heure de début
#	- son heure de fin
#	- l'heure médiane
#	- la durée de l'évenement
#	- une position centrale avec une longitude et une latitude
#		(on somme toutes les latitudes et toutes les longitude entre elles et on divise par le nombre de tweets -> on fait une moyenne pour avoir le centre de l'événement)
#	- une distance angulaire qui est le maximum de toutes les distances angulaire des tweets de l'evenement -> similiratité inter-groupe
#	- le nombre d'utilisateurs differents qui ont tweeté dans cet evenement (1 ou plrs tweets)
#	- la liste de tous les hashtags significatifs
#
import uuid
from Position import Position

class Event :
    def __init__(self,tweets, blacklist= []) :
        self.tweets=sorted(tweets,key=lambda tweet : tweet.time)
        
        self.eventStartingTime=self.tweets[0].time
        self.eventEndingTime=self.tweets[0].time
        self.eventMedianTime=self.tweets[len(tweets)/2].time
        self.estimatedEventDuration=self.tweets[len(tweets)/10].delay(self.tweets[(9*len(tweets))/10])

        userIdSet=set()
	#----- Calcul du centre (latitude,longitude) -----#
        self.eventCenter=Position(0,0)
        for tweet in tweets :
            userIdSet.add(tweet.userId)
            self.eventCenter.latitude+=tweet.position.latitude
            self.eventCenter.longitude+=tweet.position.longitude
            if (tweet.time<self.eventStartingTime) :
                self.eventStartingTime=tweet.time
            elif (tweet.time>self.eventEndingTime) :
                self.eventEndingTime=tweet.time
        self.eventCenter.latitude/=len(tweets)
        self.eventCenter.longitude/=len(tweets)
		
	#---- Calcul de la distance angulaire maximale -----#
        self.eventRadius=self.eventCenter.distance(tweets[0].position)
        for tweet in tweets :
            distance=self.eventCenter.distance(tweet.position)
            if (distance>self.eventRadius) :
                self.eventRadius=distance
                
        self.userNumber=len(userIdSet)        
        self.importantHashtags=self.getImportantHashtags(20, blacklist)
        self.hashtags=self.getImportantHashtags(20, blacklist, False)

    #----------------------------------------------------------------------------------------------------#
        
    def getImportantHashtags(self, topk=10, blacklist=[], onlyImportant = True) :
	    # on compte le nbr d'apparitions d'un mot dans toutes les listes d'hashtags des tweets de l'evenement
        dictHashtags={}
        for t in self.tweets :
            for h in t.hashtags :
                if (h.lower() not in blacklist):
                    try : dictHashtags[h.lower()]+=1
                    except KeyError : dictHashtags[h.lower()]=1
				
        # on renvoie la liste de tous les hashtags recuperes, on les range dans l'ordre décroissant grace à leur nbr d'occurrence
        # et on ne garde que les 'topk' premiers hashtags de cette liste pour avoir les 'topk' hashtags les plus frequents
        # attention si on a moins de topk hashtags on les renvoie tous
        importantHashtags = []
        if (onlyImportant):
            importantHashtags=sorted(list(dictHashtags), key=lambda element : dictHashtags[element], reverse=True)[0:min(topk,len(dictHashtags))]
        else:
            importantHashtags = sorted(list(dictHashtags), key=lambda element: dictHashtags[element], reverse=True)

        return importantHashtags

    # ----------------------------------- Output for vizualisation -------------------------------------#
    
    def outForVizu(self):
        SEPARATOR = ","
        NUM_DIGIT=10**2
        position = Position(self.eventCenter.latitude,self.eventCenter.longitude)
        S = SEPARATOR.join([
                           str(uuid.uuid4()),
                           str(self.eventMedianTime),
                           str(int(self.estimatedEventDuration)),
                           position.str2(),
                           str(float(int(NUM_DIGIT * self.eventRadius)) / NUM_DIGIT),
                           str(self.userNumber),
                           str(len(self.tweets)),
                           "|".join(self.hashtags)])
        return S.encode("utf-8")

    #---------------- Visualize -----------------------------------------------------------------------#
    
    def __str__(self) :
        NUM_DIGIT=10**2
        SEPARATOR="\n|"
        position = Position(self.eventCenter.latitude,self.eventCenter.longitude)
        S="->"+SEPARATOR.join(["Temps median : " + str(self.eventMedianTime),
                              "Duree estimee : " + str(int(self.estimatedEventDuration)),
                              "Position du centre de l'event : " + str(position),
                              "Rayon de l'event : " + str(float(int(NUM_DIGIT*self.eventRadius))/NUM_DIGIT),
                              "Nombre de twittos : " + str(self.userNumber),
                              "Nombre de tweets : " + str(len(self.tweets)),
                              "Hashtags importants : " + ",".join(self.importantHashtags)])+SEPARATOR
        return S.encode("utf-8")
    #----------------------------------------------------------------------------------------------------#
