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

class TabnakSpider(scrapy.Spider):
    name = "Tabnak_spider"
    allowed_domains = ['Tabnak.ir']

    if rss_reader('https://www.tabnak.ir/fa/rss/allnews') == 'Success':
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

        title = response.xpath('//h1[@class="Htag"]/a/text()').get()
        dic["title"] = title

        news_url = response.css('h1[class=Htag] a::attr(href)').extract()[0]
        dic["url"] = "https://www.tabnak.ir" + news_url

        sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
        final_sections = []
        for sec in sections:
            processed_text = " ".join(sec.split())
            final_sections.append(processed_text)

        dic["article_section"] = final_sections

        summary = response.xpath('//div[@class="subtitle"]/text()').getall()
        dic["summary"] = summary[1]


        date = response.xpath('//sapn[@class="fa_date"]/text()').get()
        date_list = date.split(' ')
        # print(date_list)
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

        code = response.xpath('//div[@class="news_id_c"]/text()').get()
        dic["code"] = " ".join(code.split())

        tags = response.xpath('//div[@class="tag_items"]/a/text()').getall()
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
