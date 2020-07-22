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
    filename="spider17.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)

class RooznoSpider(scrapy.Spider):
    name = "Roozno_spider"
    allowed_domains = ['roozno.com']

    if rss_reader('http://roozno.com/fa/rss/1') == 'Success':
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

        title = response.xpath('//h1[@class="title"]/a/text()').get()
        dic["title"] = title

        news_url = response.css('h1[class=title] a::attr(href)').extract()[0]
        dic["url"] = "https://roozno.com" + news_url

        sections = []
        dic["article_section"] = sections

        summary = response.xpath('//div[@class="subtitle"]/text()').get()
        if summary == None:
            dic["summary"] = summary
        else:
            dic["summary"] = " ".join(summary.split(' '))

        date = response.xpath('//div[@class="news_nav news_pdate_c col-xs-36 col-sm-14"]/span/text()').getall()
        date = date[1]
        date_list = date.split(' ')
        print(date_list)
        time_list = date_list[0].split(':')
        hour = convert_persian_to_english_numbers(time_list[0])
        minute = convert_persian_to_english_numbers(time_list[1])

        day = convert_persian_to_english_numbers(date_list[2])
        month = month_dic[date_list[3]]
        year = convert_persian_to_english_numbers(date_list[4])
        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))
        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        code = response.xpath('//div[@class="news_nav news_id_c col-xs-36 col-sm-11"]/text()').get()
        dic["code"] = code

        tags = response.xpath('//div[@class="tags_title"]/a/text()').getall()
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
