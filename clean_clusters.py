from pymongo import MongoClient
import datetime

print("process started at at :")
print(datetime.datetime.now())
client = MongoClient()
db = client['webdb']

articles_tfidf = db.tfidfclusters
articles_w2v = db.w2vclusters

countt = 0
for a in articles_tfidf.find():
    countt += 1
countw = 0
for a in articles_w2v.find():
    countw += 1

print("num of tfidf clusters :")
print(str(countt) + "\n")

print("num of w2v clusters :")
print(str(countw) + "\n")



remove_list = []
count2 = 0
for a in articles_tfidf.find():
    if a["numofnews"] < 2 and articles_w2v.find_one({"list": a["list"]}) is not None:
        remove_list.append(a["list"])
        count2 += 1

print("removed number :")
print(str(count2) + "\n")
for num in remove_list:
    myquery = {"list": num}
    articles_tfidf.delete_one(myquery)
    articles_w2v.delete_one(myquery)

countt = 0
for a in articles_tfidf.find():
    countt += 1
countw = 0
for a in articles_w2v.find():
    countw += 1

print("num of tfidf clusters :")
print(str(countt) + "\n")

print("num of w2v clusters :")
print(str(countw) + "\n")

