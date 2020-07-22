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
    filename="./logs/spider3.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)


class KhabarOnlineSpider(scrapy.Spider):
    name = "khabarOnline_spider"
    allowed_domains = ['khabaronline.ir']

    if rss_reader('https://www.khabaronline.ir/rss') == 'Success':
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

        item_body_SELECTOR = '.item-body'
        text = " "
        dic = {"timestamp":"", "url" : " " , "title" : " ", "text" : " ", "summary" : " " , "tags": [] , "article_section" : " ", "code" : " "}

        title = response.xpath('//h1[@class="title"]/a/text()').get()
        dic["title"] = title
        dic["preprocessed_title"] = preprocess(dic["title"])

        news_url = response.xpath('//meta[@name="twitter:url"]').xpath('@content').get()
        dic["url"] = news_url

        article_section = response.xpath('//meta[@property="article:section"]').xpath('@content').getall()
        dic["article_section"] = article_section


        item_summary_SELECTOR = '.item-summary p ::text'
        if (response.css(item_summary_SELECTOR).extract()) :
            dic["summary"] = response.css(item_summary_SELECTOR).extract()[0]
            dic["preprocessed_summary"] = preprocess(dic["summary"])

        date = response.xpath('//div[@class="barcode"]/ul/li[@class="date"]/text()').get()
        if date == None:
            date = response.xpath('//div[@class="item-date"]/span/text()').get()
        list = date.split(' ')
        # print(list)
        day = convert_persian_to_english_numbers(list[0])
        month = month_dic[list[1]]
        year = convert_persian_to_english_numbers(list[2])
        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        time = list[4]
        # print(convert_persian_to_english_numbers(day))
        # print(month_dic[month])
        # print(convert_persian_to_english_numbers(year))

        list_time = time.split(':')
        hour = convert_persian_to_english_numbers(list_time[0])
        minute = convert_persian_to_english_numbers(list_time[1])
        # print(convert_persian_to_english_numbers(hour))
        # print(convert_persian_to_english_numbers(minute))
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))

        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        code = response.xpath('//div[@class="barcode"]/ul/li[@class="id"]/span/text()').get()
        if code == None:
            code = response.xpath('//input[@id="newsId"]').xpath('@value').get()
        dic["code"] = code

        tags = response.xpath('//section[@class="box tags"]/div/ul/li/a/text()').getall()



        for brickset in response.css(item_body_SELECTOR):
            item_text_SELECTOR = '.item-text p ::text'
            paragraphs = brickset.css(item_text_SELECTOR).extract()
            for i in range(0,len(paragraphs)-1):
                text = text + '\n' + paragraphs[i]

        dic["text"] = text

        dic["tags"] = tags

        dic["preprocessed_text"] = preprocess(dic["text"])
        dic["w2v"] = get_word2vec(dic).tolist()
        dic["tfidf"] = get_tfidt_vector(dic).tolist()

        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        res = es.index(index='newsindex', doc_type='news', body=dic)

        client = MongoClient()
        db = client['newsdb_week']
        articles = db.weekarticles
        result = articles.insert_one(dic)
