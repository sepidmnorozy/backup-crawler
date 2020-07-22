from pymongo import MongoClient
import datetime
client = MongoClient()
src_db = client['newsdb_week']
articles = src_db.weekarticles
print(articles.count_documents({}))

print("num of wanted")
x = datetime.datetime(2020, 2, 13, 0, 0, 0)
y = datetime.datetime(2020, 2, 14, 0, 0, 0)

print(articles.count_documents({"timestamp": {"$lt": y.timestamp(),"$gt": x.timestamp()}}))
#for doc in cursor:
 #   count = count + 1

 #   if "title" in doc and doc["title"] != None and " کرونا " in doc["title"]:
  #      count = count + 1
   #     continue
   # if "text" in doc and doc["text"] != None and " کرونا " in doc["text"]:
    #    count = count + 1
     #   continue
    #if "summary" in doc and doc["summary"] != None and " کرونا " in doc["summary"]:
     #   count = count + 1
      #  continue
#print(count)
#file = open("momres.txt", "w")
#file.write(str(count))
#file.close()
