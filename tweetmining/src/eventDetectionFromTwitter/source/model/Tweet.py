import re,string

class Tweet :
    def __init__(self,_id,userId,text,hashtags,time,position=None) :
        self.id=_id
        self.userId=userId
        self.text=text.replace("\"", "")
        #self.hashtags=' '.join(re.sub("(@[A-Za-z0-9]+)", "", hashtags.replace("\"", "")).split()).split()
        self.hashtags=hashtags.replace("\"", "")
        self.time=time
        self.position=position

    def delay(self,other) :
        return abs((self.time-other.time).total_seconds())

    def __str__(self) :
        return "{0} : ({1},{2}), #: {3}".format(self.id,self.time,self.position, self.hashtags)
