from pymongo import MongoClient
import datetime


print("saving clusters started at :")
print(datetime.datetime.now())

client = MongoClient()

src_db = client['webdb']
w2vclusters = src_db.w2vclusters
tfidfclusters = src_db.tfidfclusters


dst_db = client['evaldb']
eval = dst_db.evalclusters


list1 = []
list2 = []
count = 0
for a in w2vclusters.find({}):
    list1.append(a["list"])
    count += 1
print(count)
count = 0
for a in tfidfclusters.find({}):
    list2.append(a["list"])
    count += 1
print(count)
now = datetime.datetime.now()
dic1 = {"time": str(now), "type":"w2v", "list":list1}
eval.insert_one(dic1)

dic2 = {"time": str(now), "type":"tfidf", "list":list2}
eval.insert_one(dic2)



print("saving clusters finished at :")
print(datetime.datetime.now())

