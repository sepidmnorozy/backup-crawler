from pymongo import MongoClient
import numpy as np
from preprocess import preprocess
# from word2vec import get_word2vec
from tfidf import get_tfidt_vector
import datetime


def similarity(vec, other_vec):
   dot = np.dot(vec, other_vec)
   norma = np.linalg.norm(vec)
   normb = np.linalg.norm(other_vec)
   cos = dot / (norma * normb)
   return cos


def search(text):
   try:
       articles = db.articles
       print("got search text")
       search_text =  preprocess(text)
       print("done preprocess")
       # search_text_tokens = search_text.split(' ')
       # print("got tokens")
       dic = {"preprocessed_text": search_text}
       # search_v_w2v =  get_word2vec(dic)
       # print("search vector w2v")
       search_v_tfidf =  get_tfidt_vector(dic)
       print("search vector tfidf")
       print(search_v_tfidf)
       if np.all(search_v_tfidf == 0):
           return 0
       now = datetime.datetime.now()
       result_w2v_list = []
       result_tfidf_list = []
       result_exact_list = []
       print("lists created")
       count = 0
       for a in articles.find():
           count += 1
       # for a in articles.find({"timestamp": {"$gt": now.timestamp() - 172800.0}}):
       #     if np.all(np.array(a["tfidf"]) == 0):
       #         # print("ahhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
           # if np.all(np.array(a["w2v"])!=0) and np.all(search_v_w2v!=0):
           #     # print("hi")
           #     if similarity(np.array(a["w2v"]), search_v_w2v) > 0.8:
           #         result_w2v_list.append(a)
           if not np.all(np.array(a["tfidf"]) == 0) and not np.all(search_v_tfidf == 0):
               print("hi")
               if similarity(np.array(a["tfidf"]), search_v_tfidf) > 0.2:
                   result_tfidf_list.append(a)
           # for token in search_text_tokens:
           #     if token in a["text"]:
           #         result_exact_list.append(a)
           #         break
       print("num of documents checked : ")
       print(count)
       print(len(result_tfidf_list))
       print(len(result_w2v_list))
       print(len(result_exact_list))


       file = open("searchresult.txt","w")
       res = "search text : \n\n" + text + "\n\n"+ "tfidt : \n\n"

       for r in result_tfidf_list:
           res += r["url"] + "\n"
           if "title" in r :
               res += r["title"] + "\n"
           if "text" in r:
               res += r["text"] + "\n"
       res += "word2vec : \n\n"
       for r in result_w2v_list:
           res += r["url"] + "\n"
           if "title" in r:
               res += r["title"] + "\n"
           if "text" in r:
               res += r["text"] + "\n"
       res += "exact : \n\n"
       for r in result_exact_list:
           res += r["url"] + "\n"
           if "title" in r:
               res += r["title"] + "\n"
           if "text" in r:
               res += r["text"] + "\n"
       file.write(res)
       file.close()
       return 1
   except(Exception):
       return 0


print("hi1")
client = MongoClient()
db = client['newsdb']
#
searchstatus = db.searchstatus

# mydict = {"status": "ready"}
# x = searchstatus.insert_one(mydict)
# print("first done")

status = ''

print("hi2")


#Change Streams
txt = "ای قوم به حج رفته"
print(search(txt))


