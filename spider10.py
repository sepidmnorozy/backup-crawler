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
    filename="spider10.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)

class FarsSpider(scrapy.Spider):
    name = "Fars_spider"
    allowed_domains = ['farsnews.com']

    if rss_reader('https://www.farsnews.com/rss') == 'Success':
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

        title = response.xpath('//span[@class="title mb-2 d-block text-justify"]/text()').get()
        dic["title"] = title

        news_url = response.css('link[rel=canonical]::attr(href)').extract()[0]
        dic["url"] = news_url

        sections = response.xpath('//div[@class="category-name d-flex justify-content-center"]/span/a/text()').getall()
        final = []
        for s in sections:
            processed_text = " ".join(s.split())
            final.append(processed_text)
        dic["article_section"] = final

        summary = response.xpath('//p[@class="lead p-2 text-justify"]/text()').get()
        dic["summary"] = summary

        date = response.xpath('//div[@class="publish-time d-flex justify-content-center"]/span/text()').getall()
        if len(date) > 1:
            timelist = date[0].split(':')
            hour = convert_persian_to_english_numbers(timelist[0])
            minute = convert_persian_to_english_numbers(timelist[1])

            date_list = date[2].split('/')

            day = convert_persian_to_english_numbers(date_list[2])

            month = convert_persian_to_english_numbers(date_list[1])

            yearlist = date_list[0].split('،')

            year = convert_persian_to_english_numbers(yearlist[0])

            jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()

            datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                                int(minute))

            dic["date"] = str(datetime_object)
        else:
            date = response.xpath('//span[@class="publish-time text-center"]/text()').get()
            date_list = date.split(' ')

            timelist = date_list[2].split(':')
            hour = convert_persian_to_english_numbers(timelist[0])
            minute = convert_persian_to_english_numbers(timelist[1])

            d_list = date_list[0].split('/')

            day = convert_persian_to_english_numbers(d_list[2])

            month = convert_persian_to_english_numbers(d_list[1])

            year = convert_persian_to_english_numbers(d_list[0])

            jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()

            datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                                int(minute))

            dic["date"] = datetime_object

        #
        #
        dic["timestamp"] = datetime_object.timestamp()
        code = ''
        dic["code"] = code

        tags = response.xpath('//div[@class="tags mt-4 text-right d-flex flex-wrap"]/a/text()').getall()
        finaltags = []
        for t in tags:
            processed_text = " ".join(t.split())
            finaltags.append(processed_text)
        dic["tags"] = finaltags
        #
        text_list = response.xpath('//div[@class="nt-body text-right mt-4"]/p/text()').getall()
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
