from pymongo import MongoClient
from preprocess import preprocess
from word2vec import get_word2vec
from tfidf import get_tfidt_vector


def add_vector_for_old_news():
    client = MongoClient()
    db = client['newsdb']
    articles = db.articles
    # count = 0
    # b = {}
    # a = {"id":1}
    # b = a
    # print(b)
    # b["text"] = "salam"
    # print(b)
    all_news_list = []
    count_of_ah = 0
    for a in articles.find():
        b = a
        # if "title" in a :
        #     b["preprocessed_title"] = preprocess(a["title"])
        if "summary" in a :
            b["preprocessed_summary"] = preprocess(a["summary"])

        w2v_vector = get_word2vec(b).tolist()
        tfidf_vector = get_tfidt_vector(b).tolist()
        b["w2v"] = w2v_vector
        b["tfidf"] = tfidf_vector
        all_news_list.append(b)
        print("done")

    print("first step done")
    articles.delete_many({})
    print("second step done")
    for dic in all_news_list:
        articles.insert_one(dic)
    print("third step done")



add_vector_for_old_news()