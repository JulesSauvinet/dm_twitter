# coding=utf-8
# Ce module permet de construire un Tweet, jusque la, rien d'extraordinaire
#
# Pour décrire un Tweet on récupère l'identifiant + la personne qui a tweet + le texte + les hashtags + l'heure du tweet 
# et pour finir la position de la personne qui a poste le tweet.
#

import re,string

class Tweet :
    def __init__(self,_id,userId,text,hashtags,time,position=None) :
        self.id=_id 
        self.userId=userId
        self.text=text.replace("\"", "")
        #self.hashtags=' '.join(re.sub("(@[A-Za-z0-9]+)", "", hashtags.replace("\"", "")).split()).split()
        if (isinstance(hashtags,list)) :
            self.hashtags=hashtags
        else :
            self.hashtags=' '.join(re.sub("(@[A-Za-z0-9]+)", "", hashtags.replace("\"", "")).split()).split()
        self.time=time
        self.position=position
        self.lat = None
        self.long= None

    def delay(self,other) :
        return abs((self.time-other.time).total_seconds())

    def __str__(self) :
        return "{0} : ({1},{2}), #: {3}".format(self.id,self.time,self.position, self.hashtags)
