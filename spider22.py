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

class BehdashtSpider(scrapy.Spider):
    name = "Behdasht_spider"
    allowed_domains = ['behdasht.gov.ir']

    if rss_reader('https://behdasht.gov.ir/rss') == 'Success':
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

        dic = {"title":" "}

        title = response.xpath('//div[@class="news-head"]/h6/text()').get()
        title += response.xpath('//div[@class="news-head"]/h2/text()').get()
        dic["title"] = title

        news_url = response.xpath('//*[@id="st-container"]/div/div/div/main/div[1]/div/div/div/ul/li[3]/a/@href').extract()[0]
        dic["url"] = "http://behdasht.gov.ir"+news_url

        # news_path
        sections = response.xpath('//*[@id="page-content"]/div/article/div/div[2]/div/div/ul/li[1]/text()').getall()
        dic["article_section"] = sections[2]

        summary = response.xpath('//div[@class="news-lead"]/p/text()').get()
        dic["summary"] = summary

        date = response.xpath('//*[@id="page-content"]/div/div[1]/div/div[1]/div/ul/li[1]/span/text()').get()
        date_list = date.split(' ')
        # print(date_list)
        timelist = date_list[5].split(':')
        hour = timelist[0]
        # print(hour)
        minute = timelist[1]
        # print(minute)
        #
        date_list = date_list[0].split("/")
        # print(date_list)
        day = date_list[2]
        month = date_list[1]
        year = date_list[0]
        jalili_date = jdatetime.date(1300 + int(year), int(month), int(day)).togregorian()
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))
        
        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        code = response.xpath('//*[@id="page-content"]/div/article/div/div[2]/div/div/ul/li[2]/text()').getall()
        dic["code"] = code[2]

        tags = response.xpath('//div[@class="es-news-tags"]/ul/li/a/text()').getall()
        dic["tags"] = tags

        text_list = response.xpath('//div[@class="news-content"]/div/text()').getall()
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
