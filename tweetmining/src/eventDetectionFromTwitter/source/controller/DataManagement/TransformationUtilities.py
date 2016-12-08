import json
from ...model.Tweet import Tweet
from ...model.Position import Position
from datetime import date, datetime
import moment

#-------------------------------------------------------------
def getTweetFromJSON(jsonText) :
    jsonData = json.loads(jsonText)
    _id=jsonData["id"]
    userId=jsonData['user']['id']
    text=jsonData["text"]
    #---- Hashtags ----------------------------------
    hashtags=[element["text"] for element in jsonData["entities"]["hashtags"]]
    #------------------------------------------------
    s=jsonData["created_at"]

    time=s#parser.parse(s)
    #-----Position ----------------------------------
    position=None
    if jsonData["coordinates"] :
        latitude=jsonData["coordinates"]["coordinates"][1]
        longitude=jsonData["coordinates"]["coordinates"][0]
        position=Position(latitude,longitude)
    return Tweet(_id,userId,text,hashtags,time,position)

#-------------------------------------------------------------
def getTweetFromJSONFile(jsonFilePath) :
    with open(jsonFilePath) as f :
        return getTweetFromJSON(f.readline())
#-------------------------------------------------------------
#-------------------------------------------------------------
def getTweetFromCSVLine(tweetLine) :
    attributes = tweetLine.split(",")
    _id=attributes[0]
    #print _id
    userId=attributes[10]
    text=attributes[9]
    hashtags=attributes[9]
    #------------------------------------------------
    s=attributes[5]+attributes[4]+attributes[3]+"T"+attributes[2]+attributes[1]
    timestring = datetime(int(attributes[5]),int(attributes[4]),int(attributes[3]),int(attributes[2]),int(attributes[1]))
    time = timestring #moment.date(timestring, '%Y%m%dT%H%M')
    #-----Position ----------------------------------
    position=None
    if (attributes[6]!= "null" and attributes[7]!= "null") :
        latitude=attributes[6]
        longitude=attributes[7]
        position=Position(latitude,longitude)

    return Tweet(_id,userId,text,text,hashtags,position)

