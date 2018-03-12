import pymongo
import operator

# Creating a mongo database to store the requested data
client = pymongo.MongoClient()
# Database name is minedNews
db = client.climate_change
# Collection name (db Table)
currentCol = db.climate_articles

# Getting all the names of the websites we got text from
sitesDict = {}

for doc in currentCol.find():
    if doc["siteName"] not in sitesDict:
        sitesDict[doc["siteName"]] = 1
    else:
        sitesDict[doc["siteName"]] += 1

# dictionary sorted by key, the result is a list of tuples
keySorted = sorted(sitesDict.items(), key=operator.itemgetter(0))
# dictionary sorted by value, the result is a list of tuples
valueSorted = sorted(sitesDict.items(), key=operator.itemgetter(1))

# printing the dictionary
for (key, value) in valueSorted:
    print(key + ": " + str(sitesDict[key]))
    # Inserting into a mongodb collection (sitesContributions)
    #db.sitesContributions.insert({"siteName": key, "timesVisited": value})
