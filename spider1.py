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
    filename="./logs/spider1.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)



class SpiderAsriran(scrapy.Spider):
    name = "Asriranonline_spider"
    allowed_domains = ['asriran.com']

#    print("*************************************************************************************")
#    print("HI")
#    print("*************************************************************************************")
    if rss_reader('https://www.asriran.com/fa/rss/allnews') == 'Success':
        with open("links.json", 'r') as f:
            urls = json.load(f)
    else:
        urls = []
#    print("*************************************************************************************")
#    print(urls)
#    print("*************************************************************************************")
    client = MongoClient()
    db = client['newsdb_week']
    articles = db.weekarticles
    start_urls = []
    # print("********")
    # print(urls)
    # print("********")
    now = datetime.datetime.now()
    for url in urls:
#        if articles.find_one({"url": url}) is None:
        if articles.find_one({"timestamp": {"$gt": now.timestamp() - 86400.0}, "url": url}) is None:
            start_urls.append(url)

    def parse(self, response):

        dic = {"timestamp": " ","title": " ", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [],
                    "article_section": " ", "preprocessed_text": " ", "w2v": [], "tfidf": [], "code": " "}


        title = response.xpath('//h1[@class="title"]/a/text()').get()
        dic["title"] = title
        dic["preprocessed_title"] = preprocess(dic["title"])


        news_url = response.css('h1[class=title] a::attr(href)').extract()
        if len(news_url) > 0:
            news_url = news_url[0]
        dic["url"] = "https://www.asriran.com"+news_url


        sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
        dic["article_section"] = sections[1:]


        summary = response.xpath('//div[@class="subtitle"]/text()').get()
        dic["summary"] = summary
        dic["preprocessed_summary"] = preprocess(dic["summary"])

        date_list = response.xpath('//div[@class="news_nav news_pdate_c"]/text()').getall()

        if len(date_list) > 0:
            date = ""
            for d in date_list:
                date += d
            newdate = ''.join(date.split())
            list = newdate.split('-')
            justdate = list[1]
            justtime = list[0]
        else:
            date = response.xpath('//div[@class="update_date"]/text()').getall()[0]
            newdatetmp = ''.join(date.split())
            tmp = newdatetmp.split(":")
            newdate = ':'.join(tmp[1:])
            list = newdate.split('-')
            justdate = list[0]
            justtime = list[1]

        timelist = justtime.split(':')
        hour = convert_persian_to_english_numbers(timelist[0])
        minute = convert_persian_to_english_numbers(timelist[1])
        # print(hour)
        # print(minute)
        index = 0
        for char in justdate:
            if char not in num_dic:
                index = justdate.index(char)
                break
        day = convert_persian_to_english_numbers(justdate[0:index])
        monthandyear = justdate[index:]


        for char in monthandyear:
            if char in num_dic:
                index = monthandyear.index(char)
                break

        month = month_dic[monthandyear[0:index]]
        year = convert_persian_to_english_numbers(monthandyear[index:])
        # print(month)
        # print(year)
        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        # print(jalili_date)
        datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
                                            int(minute))
        # print(datetime_object)

        dic["date"] = str(datetime_object)

        dic["timestamp"] = datetime_object.timestamp()

        code_list = response.xpath('//div[@class="news_nav news_id_c"]/text()').getall()
        code = ""
        for c in code_list:
            code += c
        dic["code"] = code

        tags = response.xpath('//div[@class="tags_title"]/a/text()').getall()
        dic["tags"] = tags

        text_parts = response.xpath('//div[@class="body"]/p/text()').getall()

        text = ""
        for text_part in text_parts:
            text += text_part

        if (len(text) < 1):
            maybe_div = response.xpath('//div[@class="body"]/div/text()').getall()
            for d in maybe_div:
                text += d
            maybe_p = response.xpath('//div[@class="body"]/p/text()').getall()
            for p in maybe_p:
                text += p
            maybe_s = response.xpath('//div[@class="body"]/p/span/text()').getall()
            for s in maybe_s:
                text += s

        dic["text"] = text


        dic["preprocessed_text"] = preprocess(dic["text"])
        dic["w2v"] = get_word2vec(dic).tolist()
        dic["tfidf"] = get_tfidt_vector(dic).tolist()

        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        res = es.index(index='newsindex', doc_type='news', body=dic)


        client = MongoClient()
        db = client['newsdb_week']
        articles = db.weekarticles
        articles.insert_one(dic)

        print("**********************************************************************************************************")
        print(dic["url"])
        print("**********************************************************************************************************")





# class YJCSpider(scrapy.Spider):
#     name = "YJCSpider"
#     allowed_domains = ['yjc.ir']
#
#     if rss_reader('https://www.yjc.ir/fa/rss/allnews') == 'Success':
#         with open("links.json", 'r') as f:
#             urls = json.load(f)
#     else:
#         urls = []
#
#
#     client = MongoClient()
#     db = client['newsdb']
#     articles = db.articles
#     start_urls = []
#     # print("********")
#     # print(urls)
#     # print("********")
#     for url in urls:
#         if articles.find_one({"url": url}) is None:
#             start_urls.append(url)
#
#     def parse(self, response):
#         dic = {"timestamp": "", "title": " ", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ",
#                "code": " "}
#
#         title = response.xpath('//h1[@class="Htags"]/a/text()').get()
#         dic["title"] = title
#
#         news_url = response.css('h1[class=Htags] a::attr(href)').extract()
#         if len(news_url)>0:
#             news_url=news_url[0]
#         dic["url"] = "https://www.yjc.ir"+news_url
#
#         sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
#         dic["article_section"] = sections
#
#         summary = response.xpath('//strong[@class="news_strong"]/text()').get()
#         dic["summary"] = summary
#
#         date_list = response.xpath('//div[@class="news_nav news_pdate_c"]/text()').getall()
#         date = ""
#         for d in date_list:
#             date += d
#         list = date.split(' ')
#         # print(list)
#         day = convert_persian_to_english_numbers(list[0])
#         month = month_dic[list[1]]
#         year = convert_persian_to_english_numbers(list[2])
#         jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
#         time = list[4]
#         # print(convert_persian_to_english_numbers(day))
#         # print(month_dic[month])
#         # print(convert_persian_to_english_numbers(year))
#
#         list_time = time.split(':')
#         hour = convert_persian_to_english_numbers(list_time[0])
#         minute = convert_persian_to_english_numbers(list_time[1])
#         # print(convert_persian_to_english_numbers(hour))
#         # print(convert_persian_to_english_numbers(minute))
#         datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
#                                             int(minute))
#
#         dic["date"] = str(datetime_object)
#
#         dic["timestamp"] = datetime_object.timestamp()
#
#         code_list = response.xpath('//div[@class="news_nav news_id_c"]/text()').getall()
#         code = ""
#         for c in code_list:
#             code += c
#         dic["code"] = code
#
#         tags = response.xpath('//div[@class="tag_items"]/a/text()').getall()
#         dic["tags"] = tags
#
#         text_parts = response.xpath('//div[@class="body"]/p/text()').getall()
#
#         text = ""
#         for text_part in text_parts:
#             text += text_part
#
#         dic["text"] = text
#
#         dic["preprocessed_text"] = preprocess(dic["text"])
#         dic["w2v"] = get_word2vec(dic).tolist()
#         dic["tf-idf-v"] = get_tfidt_vector(dic).tolist()
#
#         client = MongoClient()
#         db = client['newsdb']
#         articles = db.articles
#         result = articles.insert_one(dic)
#
#
# class SpiderHamshahri(scrapy.Spider):
#     name = "Hamshahrionline_spider"
#     allowed_domains = ['hamshahrionline.ir']
#
#     if rss_reader('https://www.hamshahrionline.ir/rss') == 'Success':
#         with open("links.json", 'r') as f:
#             urls = json.load(f)
#     else:
#         urls = []
#
#
#     client = MongoClient()
#     db = client['newsdb']
#     articles = db.articles
#     start_urls = []
#     # print("********")
#     # print(urls)
#     # print("********")
#     for url in urls:
#         if articles.find_one({"url": url}) is None:
#             start_urls.append(url)
#
#     def parse(self, response):
#         dic = {"timestamp": "", "title": " ", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ",
#                "code": " "}
#
#         title = response.xpath('//h1[@class="title"]/a/text()').get()
#         dic["title"] = title
#
#         news_url = response.css('h1[class=title] a::attr(href)').extract()
#         if len(news_url)>0:
#             news_url = news_url[0]
#         dic["url"] = "https://www.hamshahrionline.ir"+news_url
#
#         sections = response.xpath('//li[@class="breadcrumb-item"]/a/text()').getall()
#         dic["article_section"] = sections[1:]
#
#         summary = response.xpath('//p[@class="introtext"]/text()').get()
#         dic["summary"] = summary
#
#         date = response.xpath('//div[@class="col-6 col-sm-4 col-xl-4 item-date"]/span/text()').get()
#         list = date.split(' ')
#         # print(list)
#         day = convert_persian_to_english_numbers(list[1])
#         month = month_dic[list[2]]
#         year = convert_persian_to_english_numbers(list[3])
#         jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
#         time = list[5]
#         # print(convert_persian_to_english_numbers(day))
#         # print(month_dic[month])
#         # print(convert_persian_to_english_numbers(year))
#
#         list_time = time.split(':')
#         hour = convert_persian_to_english_numbers(list_time[0])
#         minute = convert_persian_to_english_numbers(list_time[1])
#         # print(convert_persian_to_english_numbers(hour))
#         # print(convert_persian_to_english_numbers(minute))
#         datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
#                                             int(minute))
#
#         dic["date"] = str(datetime_object)
#
#         dic["timestamp"] = datetime_object.timestamp()
#
#         code = response.xpath('//div[@class="item-code"]/span/text()').get()
#         dic["code"] = code
#
#         tags = response.xpath('//section[@class="box tags"]/div/ul/li/a/text()').getall()
#         dic["tags"] = tags
#
#         text_parts = response.xpath('//div[@class="item-text"]/p/text()').getall()
#
#         text = ""
#         for text_part in text_parts:
#             text += text_part
#
#         dic["text"] = text
#
#         dic["preprocessed_text"] = preprocess(dic["text"])
#         dic["w2v"] = get_word2vec(dic).tolist()
#         dic["tf-idf-v"] = get_tfidt_vector(dic).tolist()
#
#         client = MongoClient()
#         db = client['newsdb']
#         articles = db.articles
#         result = articles.insert_one(dic)
#
# class KhabarOnlineSpider(scrapy.Spider):
#     name = "khabarOnline_spider"
#     allowed_domains = ['khabaronline.ir']
#
#     if rss_reader('https://www.khabaronline.ir/rss') == 'Success':
#         with open("links.json", 'r') as f:
#             urls = json.load(f)
#     else:
#         urls = []
#
#
#     client = MongoClient()
#     db = client['newsdb']
#     articles = db.articles
#     start_urls = []
#     # print("********")
#     # print(urls)
#     # print("********")
#     for url in urls:
#         if articles.find_one({"url": url}) is None:
#             start_urls.append(url)
#
#     def parse(self, response):
#
#         item_body_SELECTOR = '.item-body'
#         text = " "
#         dic = {"timestamp":"", "url" : " " , "date" : " ", "text" : " ", "summary" : " " , "tags": [] , "article_section" : " ", "code" : " "}
#
#         news_url = response.xpath('//meta[@name="twitter:url"]').xpath('@content').get()
#         dic["url"] = news_url
#
#         article_section = response.xpath('//meta[@property="article:section"]').xpath('@content').getall()
#         dic["article_section"] = article_section
#
#
#         item_summary_SELECTOR = '.item-summary p ::text'
#         if (response.css(item_summary_SELECTOR).extract()) :
#             dic["summary"] = response.css(item_summary_SELECTOR).extract()[0]
#
#         date = response.xpath('//div[@class="barcode"]/ul/li[@class="date"]/text()').get()
#         if date == None:
#             date = response.xpath('//div[@class="item-date"]/span/text()').get()
#         list = date.split(' ')
#         # print(list)
#         day = convert_persian_to_english_numbers(list[0])
#         month = month_dic[list[1]]
#         year = convert_persian_to_english_numbers(list[2])
#         jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
#         time = list[4]
#         # print(convert_persian_to_english_numbers(day))
#         # print(month_dic[month])
#         # print(convert_persian_to_english_numbers(year))
#
#         list_time = time.split(':')
#         hour = convert_persian_to_english_numbers(list_time[0])
#         minute = convert_persian_to_english_numbers(list_time[1])
#         # print(convert_persian_to_english_numbers(hour))
#         # print(convert_persian_to_english_numbers(minute))
#         datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
#                                             int(minute))
#
#         dic["date"] = str(datetime_object)
#         dic["timestamp"] = datetime_object.timestamp()
#
#         code = response.xpath('//div[@class="barcode"]/ul/li[@class="id"]/span/text()').get()
#         if code == None:
#             code = response.xpath('//input[@id="newsId"]').xpath('@value').get()
#         dic["code"] = code
#
#         tags = response.xpath('//section[@class="box tags"]/div/ul/li/a/text()').getall()
#
#
#
#         for brickset in response.css(item_body_SELECTOR):
#             item_text_SELECTOR = '.item-text p ::text'
#             paragraphs = brickset.css(item_text_SELECTOR).extract()
#             for i in range(0,len(paragraphs)-1):
#                 text = text + '\n' + paragraphs[i]
#
#         dic["text"] = text
#
#         dic["tags"] = tags
#
#         dic["preprocessed_text"] = preprocess(dic["text"])
#         dic["w2v"] = get_word2vec(dic).tolist()
#         dic["tf-idf-v"] = get_tfidt_vector(dic).tolist()
#
#         client = MongoClient()
#         db = client['newsdb']
#         articles = db.articles
#         result = articles.insert_one(dic)
#
#
# class SpiderSobhane(scrapy.Spider):
#     name = "Sobhane_spider"
#     allowed_domains = ['sobhanehonline.com']
#
#     if rss_reader('http://sobhanehonline.com/fa/rss/allnews') == 'Success':
#         with open("links.json", 'r') as f:
#             urls = json.load(f)
#     else:
#         urls = []
#
#
#     client = MongoClient()
#     db = client['newsdb']
#     articles = db.articles
#     start_urls = []
#     # print("********")
#     # print(urls)
#     # print("********")
#     for url in urls:
#         if articles.find_one({"url": url}) is None:
#             start_urls.append(url)
#
#     def parse(self, response):
#         HtmlResponse = response
#         # resfile = open('resfile_specific.html', 'w')
#         # resfile.write(str(HtmlResponse.body.decode('utf-8')))
#         # resfile.close()
#
#
#         dic = {"timestamp": "", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ", "code": " "}
#
#
#         news_url = response.css('h1[class=title] a::attr(href)').extract()
#         if len(news_url)>0:
#             news_url = news_url[0]
#         dic["url"] = "http://sobhanehonline.com"+news_url
#
#         sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
#         if len(sections) > 0:
#             dic["article_section"] = sections[0]
#
#         summary = response.xpath('//div[@class="subtitle"]/text()').get()
#         dic["summary"] = summary
#
#         date = response.xpath('//div[@class="news_nav news_pdate_c"]/text()').get()
#         list = date.split(' ')
#         # print(list)
#         day = convert_persian_to_english_numbers(list[0])
#         month = month_dic[list[1]]
#         year = convert_persian_to_english_numbers(list[2])
#         jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
#         time = list[4]
#         # print(convert_persian_to_english_numbers(day))
#         # print(month_dic[month])
#         # print(convert_persian_to_english_numbers(year))
#
#         list_time = time.split(':')
#         hour = convert_persian_to_english_numbers(list_time[0])
#         minute = convert_persian_to_english_numbers(list_time[1])
#         # print(convert_persian_to_english_numbers(hour))
#         # print(convert_persian_to_english_numbers(minute))
#         datetime_object = datetime.datetime(jalili_date.year, jalili_date.month, jalili_date.day, int(hour),
#                                             int(minute))
#
#         dic["date"] = str(datetime_object)
#         dic["timestamp"] = datetime_object.timestamp()
#
#         code = response.xpath('//div[@class="news_nav news_id_c"]/text()').get()
#         dic["code"] = code
#
#         tags = response.xpath('//a[@class="tags_item"]/text()').getall()
#         dic["tags"] = tags
#
#         text_parts = response.xpath('//div[@align="justify"]/text()').getall()
#
#         text = ""
#         for text_part in text_parts:
#             text += text_part;
#
#         if (len(text)<1):
#             maybe_text = response.xpath('//div[@class="body"]/text()').getall()
#             for t in maybe_text:
#                 text += t
#             maybe_p = response.xpath('//div[@class="body"]/p/text()').getall()
#             for p in maybe_p:
#                 text += p
#
#         dic["text"] = text
#         dic["preprocessed_text"] = preprocess(dic["text"])
#         dic["w2v"] = get_word2vec(dic).tolist()
#         dic["tf-idf-v"] = get_tfidt_vector(dic).tolist()
#
#         client = MongoClient()
#         db = client['newsdb']
#         articles = db.articles
#         result = articles.insert_one(dic)
