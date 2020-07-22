from pymongo import MongoClient, DESCENDING
import numpy as np
# import sys
import datetime


print("started at :")
print(datetime.datetime.now())

client = MongoClient()
src_db = client['newsdb_week']
articles = src_db.weekarticles

dst_db = client['webdb']
w2vclusters = dst_db.w2vclusters
tfidfclusters = dst_db.tfidfclusters
w2vclusters.delete_many({})
tfidfclusters.delete_many({})
print(w2vclusters.count_documents({}))
print(tfidfclusters.count_documents({}))
w2vclusters.create_index([("numofnews", DESCENDING)])
tfidfclusters.create_index([("numofnews", DESCENDING)])


w2vflag = 0
tfidfflag = 0

def similarity(vec, other_vec):
    dot = np.dot(vec, other_vec)
    norma = np.linalg.norm(vec)
    normb = np.linalg.norm(other_vec)
    cos = dot / (norma * normb)
    return cos


def w2vclassify(a):
    try:
        if w2vclusters.count_documents({}) == 0:
            mylist = []
            tmp = []
            tmp.append(a["url"])
            tmp.append(a["title"])
            mylist.append(tmp)
            mydic = {"num": 0, "avr": a["w2v"], "list": mylist, "numofnews": len(mylist)}
            w2vclusters.insert_one(mydic)
            # print("first one")
            # print(mydic)
        else:
            # print("check for similarity")
            num_new = w2vclusters.count_documents({})
            # print("num of current clusters")
            # print(num_new)
            num_prev = 0
            found_flag = 0
            for c in w2vclusters.find():
                list_news = c["list"]
                list_news_url = []
                for tmp in list_news:
                    list_news_url.append(tmp[0])
                if a["url"] in list_news_url:
                    continue
                else:
                    if similarity(np.array(c["avr"]), np.array(a["w2v"])) > 0.95:
                        found_flag = 1
                        num_prev = c["num"]
                        break
            if found_flag:
                myquery = {"num": num_prev}
                target = w2vclusters.find_one(myquery)
                avr = (((np.array(target["avr"]) * target["numofnews"]) + np.array(a["w2v"])) / (
                            target["numofnews"] + 1)).tolist()
                # print("target list")
                # print(target["list"])
                list = target["list"]
                tmp = []
                tmp.append(a["url"])
                tmp.append(a["title"])
                list.append(tmp)
                mydic = {"num": num_prev, "avr": avr, "list": list, "numofnews": len(list)}
                w2vclusters.delete_one(myquery)
                w2vclusters.insert_one(mydic)
            else:
                list = []
                tmp = []
                tmp.append(a["url"])
                tmp.append(a["title"])
                list.append(tmp)
                mydic = {"num": num_new, "avr": a["w2v"], "list": list, "numofnews": len(list)}
                w2vclusters.insert_one(mydic)
        return 1
    except(Exception):
        return 0


def tfidfclassify(a):
    try:
        if tfidfclusters.count_documents({}) == 0:
            mylist = []
            tmp = []
            tmp.append(a["url"])
            tmp.append(a["title"])
            mylist.append(tmp)
            mydic = {"num": 0, "avr": a["tfidf"], "list": mylist, "numofnews": len(mylist)}
            tfidfclusters.insert_one(mydic)
            # print("first one")
            # print(mydic)
        else:
            # print("check for similarity")
            num_new = tfidfclusters.count_documents({})
            # print("num of current clusters")
            # print(num_new)
            num_prev = 0
            found_flag = 0
            for c in tfidfclusters.find():
                list_news = c["list"]
                list_news_url = []
                for tmp in list_news:
                    list_news_url.append(tmp[0])
                if a["url"] in list_news_url:
                    continue
                else:
                    if similarity(np.array(c["avr"]), np.array(a["tfidf"])) > 0.8:
                        found_flag = 1
                        num_prev = c["num"]
                        break
            if found_flag:
                myquery = {"num": num_prev}
                target = tfidfclusters.find_one(myquery)
                avr = (((np.array(target["avr"]) * target["numofnews"]) + np.array(a["tfidf"])) / (
                        target["numofnews"] + 1)).tolist()
                # print("target list")
                # print(target["list"])
                list = target["list"]
                tmp = []
                tmp.append(a["url"])
                tmp.append(a["title"])
                list.append(tmp)
                mydic = {"num": num_prev, "avr": avr, "list": list, "numofnews": len(list)}
                tfidfclusters.delete_one(myquery)
                tfidfclusters.insert_one(mydic)
            if not found_flag:
                # print("no similar... create a new cluster")
                list = []
                tmp = []
                tmp.append(a["url"])
                tmp.append(a["title"])
                list.append(tmp)
                mydic = {"num": num_new, "avr": a["tfidf"], "list": list, "numofnews": len(list)}
                tfidfclusters.insert_one(mydic)
        return 1
    except(Exception):
        return 0


countw0 = 0
counttf0 = 0

now = datetime.datetime.now()
# count =
count = 0
# 86400.0
for a in articles.find({"timestamp": {"$gt": now.timestamp() - 86400.0}}):
    # print("hi")
    count += 1
    if not np.all(np.array(a["w2v"]) == 0):
        countw0 += w2vclassify(a)
    if not np.all(np.array(a["tfidf"]) == 0):
        counttf0 += tfidfclassify(a)


# a = articles.find({"timestamp": {"$gt": now.timestamp() - 172800.0}}).count()
# print(str(a))
# sys.stdout.flush()
#tfidfclusters.createIndex({ "numofnews": -1 });
#w2vclusters.createIndex({ "numofnews": -1 });


if count > 0:
    print("ok")
    print("count = " + str(count))
    print("countw0 = " + str(countw0))
    print("counttf = " + str(counttf0))
    print("finished at :")
    print(datetime.datetime.now())
    print("\n")
    # sys.stdout.flush()
else:
    print("nok")
    print("count = " + str(count))
    print("countw0 = " + str(countw0))
    print("counttf = " + str(counttf0))
    print("finished at :")
    print(datetime.datetime.now())
    print("\n")
    # sys.stdout.flush()
# print("count = "+str(count))
# print("countw0 = " + str(countw0))
# print("counttf = " + str(counttf0))
# sys.stdout.flush()

