
from pymongo import MongoClient
import datetime

print("cleaned tfidf clusters at :")
print(datetime.datetime.now())
client = MongoClient()
db = client['webdb']

articles = db.tfidfclusters
count = 0
tfidf_remove_list = []
count2 = 0
for a in articles.find():
    count += 1
    if a["numofnews"] < 2:
        tfidf_remove_list.append(a["num"])
        count2 += 1

print("num of clusters :")
print(str(count) + "\n")
print(count2)
for num in tfidf_remove_list:
    myquery = {"num": num}
    articles.delete_one(myquery)

count = 0
for a in articles.find():
    count += 1

print("num of clusters :")
print(str(count) + "\n")
