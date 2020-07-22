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

class SpiderAkhbarBank(scrapy.Spider):
    name = "AkhbarBank_spider"
    allowed_domains = ['akhbarbank.com']

    if rss_reader('http://www.akhbarbank.com/rssb5.-er48r6--4qhfle2m.puirug.r.xml') == 'Success':
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
        HtmlResponse = response
        # resfile = open('resfile_specific.html', 'w')
        # resfile.write(str(HtmlResponse.body.decode('utf-8')))
        # resfile.close()


        dic = {"title":" ", "timestamp": "", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ", "code": " "}

        title = response.xpath('//h1[@id="docDiv3TitrMain"]/text()').get()
        dic["title"] = title
        dic["preprocessed_title"] = preprocess(dic["title"])

        news_url = response.css('a[class=print-icon]::attr(href)').extract()[0]
        dic["url"] = "http://www.akhbarbank.com" + news_url.replace("/print", "")

        sections = response.xpath('//div[@class="dsinfo-p1-active"]/a/text()').getall()
        dic["article_section"] = sections

        summary = response.xpath('//div[@id="docDivLead3"]/div/text()').get()
        dic["summary"] = summary
        dic["preprocessed_summary"] = preprocess(dic["summary"])

        date = response.xpath('//div[@id="docDiv3Date"]/text()').get()
        date_list = date.split(' ')
        # print(date_list)
        timelist = date_list[5].split(':')
        hour = convert_persian_to_english_numbers(timelist[0])
        minute = convert_persian_to_english_numbers(timelist[1])
        # print("hout")
        # print(hour)
        # print("minute")
        # print(minute)

        day = convert_persian_to_english_numbers(date_list[1])
        # print("day")
        # print(day)

        month = month_dic[date_list[2]]
        # print("month")
        # print(month)

        year = convert_persian_to_english_numbers(date_list[3])
        # print("year")
        # print(year)

        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        # print(jalili_date)
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))
        # print(datetime_object)

        dic["date"] = str(datetime_object)
        dic["timestamp"] = datetime_object.timestamp()

        code = response.xpath('//div[@id="docDocID"]/text()').get()
        dic["code"] = code

        tags = []
        dic["tags"] = tags

        text_list = response.xpath('//div[@id="doctextarea"]/text()').getall()
        text = ""
        for t in text_list:
            text += t
        dic["text"] = text

        dic["preprocessed_text"] = preprocess(dic["text"])
        dic["w2v"] = get_word2vec(dic).tolist()
        dic["tfidf"] = get_tfidt_vector(dic).tolist()

        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        res = es.index(index='newsindex', doc_type='news', body=dic)

        client = MongoClient()
        db = client['newsdb_week']
        articles = db.weekarticles
        result = articles.insert_one(dic)
