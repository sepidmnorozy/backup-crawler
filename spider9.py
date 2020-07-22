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
    filename="spider9.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)

class IsnaSpider(scrapy.Spider):
    name = "Isna_spider"
    allowed_domains = ['isna.ir']

    if rss_reader('https://www.isna.ir/rss') == 'Success':
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

        dic = {"title":" ","timestamp": " ", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ", "code": " "}

        title = response.xpath('//h1[@class="first-title"]/text()').get()
        dic["title"] = title

        news_url = response.css('div[class=form-group] input::attr(value)').extract()[0]
        dic["url"] = news_url

        meta_news = response.xpath('//div[@class="meta-news"]/ul/li/span/text()').getall()

        try:
            dic["article_section"] = meta_news[3]
        except(Exception):
            dic["article_section"] = []

        summary = response.xpath('//p[@class="summary"]/text()').get()
        dic["summary"] = summary


        try:
            date = meta_news[1]
        except(Exception):
            date = response.xpath('//time/text()').get()

        date_list = date.split(' ')
        # print(date_list)
        timelist = date_list[4].split(':')
        hour = convert_persian_to_english_numbers(timelist[0])
        minute = convert_persian_to_english_numbers(timelist[1])
        # print("hour")
        # print(hour)
        # print("minute")
        # print(minute)

        day = convert_persian_to_english_numbers(date_list[0])
        # print("day")
        # print(day)
        #
        month = month_dic[date_list[1]]
        # print("month")
        # print(month)
        #

        year = convert_persian_to_english_numbers(date_list[2])
        # print("year")
        # print(year)

        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        # print(jalili_date)
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))
        # print(datetime_object)

        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        try:
            dic["code"] = meta_news[5]
        except:
            dic["code"] = ''

        tags = response.xpath('//footer[@class="tags"]/ul/li/a/text()').getall()
        dic["tags"] = tags

        text_list = response.xpath('//div[@class="item-text"]/p/text()').getall()
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
