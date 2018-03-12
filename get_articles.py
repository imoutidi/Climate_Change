import webhoseio
import pymongo
import time
from datetime import date
from clientDF import DiffbotClient

action = input("Do you want to make a new request?(Y/N): ")

# List with urls for the diffbot API
urlList = []

if action == 'Y':
    # configuring webhose request
    webhoseio.config(token="4057ff96-3ff1-4982-8c99-41d708f980ef")
    # query = "politics language:english thread.country:GB performance_score:>5"
    query = "Climate Change"
    query_params = {
        "q": "Climate Change",
        "ts": "1518278227788",
        "sort": "crawled"
    }

    output = webhoseio.query("filterWebContent", query_params)

    # getting the urls of the websites that matched our query/params
    # saving the urls to a file for verification
    outputFilename = input("Enter the name of the file which will contain the webhose urls: ")
    with open(outputFilename, 'w') as urlsOut:
        urlsOut.write("Query used: "+query+"\n\n")
        j = 0
        while output['posts']:
            i = 0
            for var in output['posts']:
                urlsOut.write(str(j)+".\n"+output['posts'][i]['url']+"\n")
                urlList.append(output['posts'][i]['url'])
                i += 1
                j += 1
            output = webhoseio.get_next()

    # Get the next batch of posts
    output = webhoseio.get_next()
elif action == 'N':
    # Reading the urls from a given file
    # !! the file must have a specific format
    fileName = input("Enter the filename which contains the urls: ")
    with open(fileName) as f:
        next(f)
        next(f)
        i = 0
        for line in f:
            if i % 2 != 0:
                urlList.append(line[:-1])
            i += 1
else:
    print("Invalid input.\n")
    exit()

# using the diffbot API to get the title, text, date, author and source of each news url

# Creating a mongo database to store the requested data
client = pymongo.MongoClient()
# Database name is minedNews
db = client.climate_change
# Collection name (db Table)
# db.climate_articles
current_date = str(date.today().year) + "-" + str(date.today().month) + "-" + \
              str(date.today().day)
weekCollection = db[current_date]

# using i to keep track the news with the corresponding urls
i = 0
blankTextCount = 0
articlesExistedCount = 0

for url in urlList:
    # setting up the request
    diffbot = DiffbotClient()
    # my diffbot token
    token = "418b4f7bef2680fdb6efe0fb92096ba2"
    api = "article"
    response = diffbot.request(url, token, api)
    print(str(i) + " " + str(response))

    # variables for creating the json string to save into the mongo db
    url = author = title = text = date = siteName = ''

    # Taking care of errors (timeout, inaccessible content )
    if 'objects' in response:
        if 'resolvedPageUrl' in  response['objects'][0]:
            url = response['objects'][0]['resolvedPageUrl']
        if 'author' in response['objects'][0]:
            author = response['objects'][0]['author']
        if 'title' in response['objects'][0]:
            title = response['objects'][0]['title']
        if 'text' in response['objects'][0]:
            text = response['objects'][0]['text']
        if 'date' in response['objects'][0]:
            date = response['objects'][0]['date']
        if 'siteName' in response['objects'][0]:
            siteName = response['objects'][0]['siteName']

        # Checking if an article already exist in collection
        findResp = weekCollection .find_one({"url": url})

        # responses that have no text are not saved into the db
        # for some reason diffbot does not identifies the text
        # even though the article does have text
        if text != '' and str(findResp) == "None":
            print("Inserting entry")
            weekCollection.insert({"url": url, "author": author,
                                   "title": title, "text": text, "date": date,
                                   "siteName": siteName})
        elif text == '':
            print("Blank text")
            blankTextCount += 1
        else:
            print("Entry already exist")
            articlesExistedCount += 1
        # one call per second
        time.sleep(1)
        i += 1

print("Blank text articles: " + str(blankTextCount))
print("Already existing articles: " + str(articlesExistedCount))