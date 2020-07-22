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

class MashreghSpider(scrapy.Spider):
    name = "Mashregh_spider"
    allowed_domains = ['mashreghnews.ir']

    if rss_reader('https://www.mashreghnews.ir/rss') == 'Success':
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

        title = response.xpath('//a[@itemprop="headline"]/text()').get()
        dic["title"] = title

        news_url = response.css('h1[class=title] a::attr(href)').extract()[0]
        dic["url"] = "https://www.mashreghnews.ir" + news_url

        sections = response.xpath('//ol[@class="breadcrumb"]/li/a/text()').getall()
        dic["article_section"] = sections

        summary = response.xpath('//p[@class="summary introtext"]/text()').get()
        dic["summary"] = summary

        date = response.xpath('//div[@class="col-xs-8 col-sm-6 item-date"]/span/text()').get()
        date_list = date.split(' ')

        timelist = date_list[4].split(':')
        hour = convert_persian_to_english_numbers(timelist[0])
        minute = convert_persian_to_english_numbers(timelist[1])

        day = convert_persian_to_english_numbers(date_list[0])

        month = month_dic[date_list[1]]

        year = convert_persian_to_english_numbers(date_list[2])

        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()

        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))

        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        code = response.xpath('//div[@class="col-xs-8 col-sm-3"]/span/text()').getall()
        dic["code"] = code

        tags = response.xpath(
            '//section[@class="box tags clean list-clean list-inline header-inline header-clean negative-margin bg-graylight"]/div/ul/li/a/text()').getall()
        dic["tags"] = tags

        text_list1 = response.xpath('//div[@class="item-text"]/p/span/text()').getall()
        text_list2 = response.xpath('//div[@class="item-text"]/p/text()').getall()
        text = ""
        for t in text_list1:
            text += t
        for t in text_list2:
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
