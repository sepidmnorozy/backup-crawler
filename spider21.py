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

class IRIBSpider(scrapy.Spider):
    name = "IRIB_spider"
    allowed_domains = ['iribnews.ir']

    if rss_reader('https://www.iribnews.ir/fa/rss/allnews') == 'Success':
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

        title = response.xpath('//h1[@class="title title_news"]/span/text()').get()
        dic["title"] = title

        news_url = response.css('h1.title_news span::attr(href)').extract()[0]
        dic["url"] = "https://www.iribnews.ir" + news_url

        sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
        dic["article_section"] = sections

        summary = response.xpath('//p[@class="subtitle"]/text()').get()
        dic["summary"] = summary

        date = response.xpath('//div[@class="news_nav news_pdate_c col-sm-16 col-xs-25"]/text()').getall()
        # dic["date"] = date
        # print("date:")
        # print(block["date"][1])
        date = date[1]
        date_list = date.split(' ')
        # print(date_list)
        timelist = date_list[21].split(':')
        hour = convert_persian_to_english_numbers(timelist[0])
        # print(hour)
        minute = convert_persian_to_english_numbers(timelist[1])
        # print(minute)
        #
        day = convert_persian_to_english_numbers(date_list[17])
        # print(day)
        month = month_dic[date_list[18]]
        # print(month)
        year = convert_persian_to_english_numbers(date_list[19])
        # print(year)
        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))
        # print(datetime_object)
        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        code = response.xpath('//div[@class="news_nav news_id_c col-sm-10  col-xs-11"]/text()').getall()
        code = " ".join(code[1].split())
        dic["code"] = code

        tags = response.xpath('//div[@class="tags_title"]/a/text()').getall()
        dic["tags"] = tags

        text_list = response.xpath('//div[@class="body body_media_content_show"]/div/text()').getall()
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
