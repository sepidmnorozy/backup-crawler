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


def search():
    client = MongoClient()
    src_db = client['newsdb_week']
    articles = src_db.weekarticles
    dst_db = client['webdb']
    searchresults = dst_db.searchresults
    # text = searches.find().sort("_id", -1)[0]["text"]
    text = sys.argv[1]
    # print("this is the text that python received")
    # print(text)

    search_text = preprocess(text)

    search_text_tokens = search_text.split(' ')
    # print("ok 1")
    dic = {"preprocessed_text": search_text}
    search_v_w2v = get_word2vec(dic)
    # print("ok 2")
    search_v_tfidf = get_tfidt_vector(dic)
    # print("ok 3")

    now = datetime.datetime.now()
    result_w2v_list = []
    result_tfidf_list = []
    result_exact_list = []

    count = 0
    count_tokens = 0
    #for a in articles.find({}):
    for a in articles.find({"timestamp": {"$gt": now.timestamp() - 2592000.0}}):
        if not np.all(search_v_w2v == 0):
            if not np.all(np.array(a["w2v"]) == 0):
               if similarity(np.array(a["w2v"]), search_v_w2v) > 0.8:
                   result_w2v_list.append(a)
            if not np.all(np.array(a["tfidf"]) == 0):
               if similarity(np.array(a["tfidf"]), search_v_tfidf) > 0.3:
                   result_tfidf_list.append(a)
            # for token in search_text_tokens:
            #     if token in a["text"]:
            #         count_tokens += 1
            #         if count_tokens == len(search_text_tokens):
            #             result_exact_list.append(a)


    # print("ok 4")
    searchresults.delete_many({})
    # print("ok 5")
    mydict = {"search_text": text, "result": result_w2v_list, "type": "w2v"}
    searchresults.insert_one(mydict)

    # print("ok 6")

    mydict = {"search_text": text, "result": result_tfidf_list, "type": "tfidf"}
    searchresults.insert_one(mydict)

    # print("ok 7")

    # mydict = {"search_text": text, "result": result_exact_list, "type": "exact"}
    # searchresults.insert_one(mydict)

    # print("ok 8")

    print("ok")
    sys.stdout.flush()
    # except(Exception):
    #     print(Exception)
    #     sys.stdout.flush()

search()
