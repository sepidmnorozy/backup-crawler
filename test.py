from pymongo import MongoClient
from rss import rss_reader
import json

if rss_reader('https://www.khabaronline.ir/rss') == 'Success':
    with open("links.json", 'r') as f:
        urls = json.load(f)
else:
    urls = []

client = MongoClient()
db = client['newsdb_week']
articles = db.weekarticles

start_urls = []
for url in urls:
    if articles.find_one({"url": url}) is None:
        start_urls.append(url)

print(start_urls)
print(len(start_urls))
