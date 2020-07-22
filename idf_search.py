from pymongo import  MongoClient
import numpy as np
from preprocess import preprocess
from word2vec import get_word2vec
from tfidf import get_tfidt_vector


client = MongoClient()
db = client['newsdb']
search_text = db.searches

articles = db.articles

search_result = db.searchresults



text = search_text.find().sort("_id", -1)[1000]["text"]

search_text = preprocess(text)
dic = {"preprocessed_text": search_text}
search_v_w2v = get_word2vec(dic)
search_v_tfidf = get_tfidt_vector(dic)

def similarity(vec, other_vec):
    dot = np.dot(vec, other_vec)
    norma = np.linalg.norm(vec)
    normb = np.linalg.norm(other_vec)
    cos = dot / (norma * normb)
    return cos


wanted_news = []




# for res in result:
#     dic = {"text": "", "similar_texts": []}
#     dic["text"] = res[0]
#     similar_texts = []
#     for i in range(1, len(res)):
#         similar_texts.append(res[i])
#     dic["similar_texts"] = similar_texts
#     similars.insert_one(dic)
#
#
# count = 0
# for a in similars.find():
#     count +=1
# print(count)