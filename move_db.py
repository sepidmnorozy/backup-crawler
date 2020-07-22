from pymongo import MongoClient
import datetime

client = MongoClient()
db = client['newsdb']
db2 = client['newsdb_week']
articles = db2.weekarticles
weekarticles = db.weekarticles

now = datetime.datetime.now()
for a in weekarticles.find({}):
    dic = {}
    if "timestamp" in a:
        dic["timestamp"] = a["timestamp"]
    if "title" in a:
        dic["title"] = a["title"]
    if "preprocessed_title" in a:
        dic["preprocessed_title"] = a["preprocessed_title"]
    if "url" in a:
        dic["url"] = a["url"]
    if "date" in a:
        dic["date"] = a["date"]
    if "text" in a:
        dic["text"] = a["text"]
    if "summary" in a:
        dic["summary"] = a["summary"]
    if "tags" in a:
        dic["tags"] = a["tags"]
    if "article_section" in a:
        dic["article_section"] = a["article_section"]
    if "preprocessed_text" in a:
        dic["preprocessed_text"] = a["preprocessed_text"]
    if "w2v" in a:
        dic["w2v"] = a["w2v"]
    if "tfidf" in a:
        dic["tfidf"] = a["tfidf"]
    if "code" in a:
        dic["code"] = a["code"]
    if "preprocessed_summary" in a:
        dic["preprocessed_summary"] = a["preprocessed_summary"]
    articles.insert_one(dic)





