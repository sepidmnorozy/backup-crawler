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
    filename="./logs/spider2.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)


class YJCSpider(scrapy.Spider):
    name = "YJCSpider"
    allowed_domains = ['yjc.ir']

    if rss_reader('https://www.yjc.ir/fa/rss/allnews') == 'Success':
        with open("links.json", 'r') as f:
            urls = json.load(f)
    else:
        urls = []


    client = MongoClient()
    db = client['newsdb']
    articles = db.weekarticles
    start_urls = []
    # print("********")
    # print(urls)
    # print("********")
    for url in urls:
        if articles.find_one({"url": url}) is None:
            start_urls.append(url)

    def parse(self, response):
        dic = {"timestamp": "", "title": " ", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ",
               "code": " "}

        title = response.xpath('//h1[@class="Htags"]/a/text()').get()
        dic["title"] = title
        dic["preprocessed_title"] = preprocess(dic["title"])

        news_url = response.css('h1[class=Htags] a::attr(href)').extract()
        if len(news_url)>0:
            news_url=news_url[0]
        dic["url"] = "https://www.yjc.ir"+news_url

        sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
        dic["article_section"] = sections

        summary = response.xpath('//strong[@class="news_strong"]/text()').get()
        dic["summary"] = summary
        dic["preprocessed_summary"] = preprocess(dic["summary"])

        date_list = response.xpath('//div[@class="news_nav news_pdate_c"]/text()').getall()
        date = ""
        for d in date_list:
            date += d
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

        code_list = response.xpath('//div[@class="news_nav news_id_c"]/text()').getall()
        code = ""
        for c in code_list:
            code += c
        dic["code"] = code

        tags = response.xpath('//div[@class="tag_items"]/a/text()').getall()
        dic["tags"] = tags

        text_parts = response.xpath('//div[@class="body"]/p/text()').getall()

        text = ""
        for text_part in text_parts:
            text += text_part

        dic["text"] = text

        dic["preprocessed_text"] = preprocess(dic["text"])
        dic["w2v"] = get_word2vec(dic).tolist()
        dic["tfidf"] = get_tfidt_vector(dic).tolist()

        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        res = es.index(index='newsindex', doc_type='news', body=dic)

        client = MongoClient()
        db = client['newsdb']
        articles = db.weekarticles
        result = articles.insert_one(dic)
