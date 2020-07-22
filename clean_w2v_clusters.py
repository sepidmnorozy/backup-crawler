from pymongo import MongoClient
import datetime

print("cleaned w2v clusters at :")
print(datetime.datetime.now())
client = MongoClient()
db = client['webdb']
#
articles = db.w2vclusters
count = 0
w2v_remove_list = []
count2 = 0
for a in articles.find():
    count += 1
    if a["numofnews"] < 2:
        w2v_remove_list.append(a["num"])
        count2 += 1

print("num of clusters :")
print(str(count) + "\n")
print(count2)
for num in w2v_remove_list:
    myquery = {"num": num}
    articles.delete_one(myquery)

count = 0
for a in articles.find():
    count += 1

print("num of clusters :")
print(str(count) + "\n")




