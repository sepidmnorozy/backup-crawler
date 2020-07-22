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
    filename="spider6.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)

class RajaSpider(scrapy.Spider):
    name = "Raja_spider"
    allowed_domains = ['rajanews.com']

    if rss_reader('http://www.rajanews.com/rss/all') == 'Success':
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
        dic = {"title":" ", "timestamp": " ", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ", "code": " "}

        title = response.xpath('//h1[@class="title"]/text()').get()
        dic["title"] = title

        
        news_url = response.css("link[rel='shortlink']::attr(href)").extract()[0]
        dic["url"] = "http://www.rajanews.com" + news_url

        sections = []
        dic["article_section"] = sections

        summary = response.xpath('//div[@class="lead"]/text()').get()
        dic["summary"] = summary

        date = response.xpath('//div[@class="created"]/span/text()').get()
        date_list = date.split(' ')
        timelist = date_list[1].split(':')
        # print(timelist)
        hour = timelist[0]
        minute = timelist[1]
        second = timelist[2]
        date_list = date_list[0].split('-')
        # print(date_list)
        day = date_list[2]
        month = date_list[1]
        year = date_list[0]
        datetime_object = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        # print(datetime_object)
        dic["date"] = datetime_object
        dic["timestamp"] = datetime_object.timestamp()

        code = response.xpath('//div[@class="news-id"]/text()').get()
        code = processed_text = " ".join(code.split())
        code_list = code.split(' ')
        dic["code"] = code


        tags = []
        dic["tags"] = tags

        text_list = response.xpath('//div[@class="body"]/div/text()').getall()
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
