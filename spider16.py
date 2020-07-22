import scrapy
from pymongo import MongoClient
import jdatetime
import datetime
import logging

import json
from my_crawler_nums import convert_persian_to_english_numbers, num_dic, month_dic
from rss import rss_reader
from preprocess import preprocess
from word2vec import get_word2vec
from tfidf import get_tfidt_vector
from elasticsearch import Elasticsearch

logging.basicConfig(
    filename="spider16.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)

class TasnimSpider(scrapy.Spider):
    name = "Tasnim_spider"
    allowed_domains = ['tn.ai', 'tasnimnews.com']

    if rss_reader('https://www.tasnimnews.com/fa/rss/feed/0/7/0/%D8%A2%D8%AE%D8%B1%DB%8C%D9%86-%D8%A7%D8%AE%D8%A8%D8%A7%D8%B1-%D8%A7%D8%AE%D8%A8%D8%A7%D8%B1-%D8%B1%D9%88%D8%B2') == 'Success':
        with open("links.json", 'r') as f:
            urls = json.load(f)
    else:
        urls = []


    client = MongoClient()
    db = client['newsdb_week']
    articles = db.weekarticles
    start_urls = []
    # print("********")
    # print(urls)
    # print("********")
    for url in urls:
        if articles.find_one({"url": url}) is None:
            start_urls.append(url)

    def parse(self, response):

        dic = {"title":" ", "timestamp": "", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ", "code": " "}

        title = response.xpath('//h1[@class="title"]/text()').get()
        dic["title"] = title

        news_url = response.xpath('//a[@id="short-link"]/text()').get()
        dic["url"] = " ".join(news_url.split())

        sections = []
        dic["article_section"] = sections

        summary = response.xpath('//h3[@class="lead"]/text()').get()
        dic["summary"] = summary

        date = response.xpath('//li[@class="time"]/text()').get()
        date_list = date.split(' ')
        timelist = date_list[5].split(':')
        hour = convert_persian_to_english_numbers(timelist[0])
        minute = convert_persian_to_english_numbers(timelist[1])
        day = convert_persian_to_english_numbers(date_list[1])
        month = month_dic[date_list[2]]
        year = convert_persian_to_english_numbers(date_list[3])
        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))
        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        code = "no code"
        dic["code"] = code

        tags = []
        dic["tags"] = tags

        text_list = response.xpath('//div[@class="story"]/p/text()').getall()
        text = ""
        for t in text_list:
            text += t
        dic["text"] = text

        dic["preprocessed_title"] = preprocess(dic["title"])
        dic["preprocessed_summary"] = preprocess(dic["summary"])
        dic["preprocessed_text"] = preprocess(dic["text"])
        dic["w2v"] = get_word2vec(dic).tolist()
        dic["tfidf"] = get_tfidt_vector(dic).tolist()

        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        res = es.index(index='newsindex', doc_type='news', body=dic)

        client = MongoClient()
        db = client['newsdb_week']
        articles = db.weekarticles
        result = articles.insert_one(dic)
