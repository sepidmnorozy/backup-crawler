from pymongo import MongoClient
import numpy as np
from preprocess import preprocess
from word2vec import get_word2vec
from tfidf import get_tfidt_vector
import datetime
import sys


def similarity(vec, other_vec):
    dot = np.dot(vec, other_vec)
    norma = np.linalg.norm(vec)
    normb = np.linalg.norm(other_vec)
    cos = dot / (norma * normb)
    return cos


def search(text):
    try:
        client = MongoClient()
        src_db = client['newsdb_week']
        #articles = src_db.searches
        dst_db = client['webdb']
        articles = src_db.weekarticles
        searchresults = dst_db.searchresults
        #text = "بازگشایی مدارس تهران"
        #print(text)
        search_text = preprocess(text)
        search_text_tokens = search_text.split(' ')
        dic = {"preprocessed_text": search_text}
        search_v_w2v = get_word2vec(dic)
        search_v_tfidf = get_tfidt_vector(dic)
        result_w2v_list = []
        result_tfidf_list = []
        result_exact_list = []
        now = datetime.datetime.now()
        count = 0
        for a in articles.find({"timestamp": {"$gt": now.timestamp() - 5184000.0}}):
            count = count + 1
        #for a in articles.find({}):
            if not np.all(search_v_w2v == 0):
                if not np.all(np.array(a["w2v"]) == 0):
                    if similarity(np.array(a["w2v"]), search_v_w2v) > 0.8:
                        result_w2v_list.append(a)
                if not np.all(np.array(a["tfidf"]) == 0):
                    if similarity(np.array(a["tfidf"]), search_v_tfidf) > 0.3:
                        result_tfidf_list.append(a)
            # for token in search_text_tokens:
            #     if token in a["text"]:
            #         result_exact_list.append(a)
            #         break
        # print("num of documents checked : ")
        # print(count)
        print(count)

        searchresults.delete_many({})
        #
        mydict = {"search_text": text, "result": result_w2v_list, "type": "w2v"}
        searchresults.insert_one(mydict)
        #
        mydict = {"search_text": text, "result": result_tfidf_list, "type": "tfidf"}
        searchresults.insert_one(mydict)
        #
        # mydict = {"search_text": text, "result": result_exact_list, "type": "exact"}
        # searchresults.insert_one(mydict)
        #
        # mydict = {"status": "done"}
        # searchstatus.insert_one(mydict)

        print("OK")
        print(len(result_tfidf_list))
        print(len(result_w2v_list))
        s = str(len(result_tfidf_list))+str(len(result_w2v_list))
        return s
    except Exception as e:
        print(e)
        print("exception occured")
        return str(e)

text_list = ["وضعیت اقتصادی در کرونا"]
file = open("log.log","a+")
for text in text_list:
    s = str(datetime.datetime.now())
    s = s + text
    s = s + search(text)
    file.write(s)

file.close()
