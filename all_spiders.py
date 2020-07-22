import scrapy
import json
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from pymongo import MongoClient
import requests
from requests.exceptions import HTTPError
import xml.etree.ElementTree as ET


import jdatetime
import datetime
import logging

logging.basicConfig(
    filename="app.log",
    filemode="a+",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s"
)

num_dic={
    '۱':'1',
    '۲':'2',
    '۳':'3',
    '۴':'4',
    '۵':'5',
    '۶':'6',
    '۷':'7',
    '۸':'8',
    '۹':'9',
    '۰':'0'
}

month_dic = {
    "فروردین":"1",
    "اردیبهشت":"2",
    "خرداد":"3",
    "تیر":"4",
    "مرداد":"5",
    "شهریور":"6",
    "مهر":"7",
    "آبان":"8",
    "آذر":"9",
    "دی":"10",
    "بهمن":"11",
    "اسفند":"12"
}

def convert_persian_to_english_numbers(persian_num):
    eng_num = ''
    for char in persian_num:
        eng_num = eng_num + num_dic[char]
    return eng_num



def rss_reader(rss_link):
    rss_links = []
    rss_links.append(rss_link)
    for url in rss_links:
        try:
            response = requests.get(url)

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            res = f'HTTP error occurred: {http_err}' # Python 3.6
            return res
        except Exception as err:
            res = f'Other error occurred: {err}'  # Python 3.6
            return res
        else:
            rss_xml = response.text
            file = open('rss.xml', 'w')
            file.write(rss_xml)
            file.close()
            tree = ET.parse('rss.xml')
            root = tree.getroot()
            links = []
            for link in root.findall("./channel/item/link"):
                links.append(link.text)
            # print(len(links))
            with open("links.json", "w") as write_file:
                json.dump(links, write_file)
            res = 'Success'
            return res


class SpiderAsriran(scrapy.Spider):
    name = "Asriranonline_spider"
    allowed_domains = ['asriran.com']


    if rss_reader('https://www.asriran.com/fa/rss/allnews') == 'Success':
        with open("links.json", 'r') as f:
            urls = json.load(f)
    else:
        urls = []


    client = MongoClient()
    db = client['newsdb']
    articles = db.articles
    start_urls = []
    # print("********")
    # print(urls)
    # print("********")
    for url in urls:
        if articles.find_one({"url": url}) is None:
            start_urls.append(url)

    def parse(self, response):

        dic = {"timestamp": " ","title": " ", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [],
               "article_section": " ",
               "code": " "}

        title = response.xpath('//h1[@class="title"]/a/text()').get()
        dic["title"] = title

        news_url = response.css('h1[class=title] a::attr(href)').extract()
        if len(news_url) > 0:
            news_url = news_url[0]
        dic["url"] = "https://www.asriran.com"+news_url

        sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
        dic["article_section"] = sections[1:]

        summary = response.xpath('//div[@class="subtitle"]/text()').get()
        dic["summary"] = summary

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

        # print(justdate)
        # print(justtime)
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

        # print(day)

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
            text += text_part;

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


        client = MongoClient()
        db = client['newsdb']
        articles = db.articles
        result = articles.insert_one(dic)




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
    articles = db.articles
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

        news_url = response.css('h1[class=Htags] a::attr(href)').extract()
        if len(news_url)>0:
            news_url=news_url[0]
        dic["url"] = "https://www.yjc.ir"+news_url

        sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
        dic["article_section"] = sections

        summary = response.xpath('//strong[@class="news_strong"]/text()').get()
        dic["summary"] = summary

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
            text += text_part;

        dic["text"] = text

        client = MongoClient()
        db = client['newsdb']
        articles = db.articles
        result = articles.insert_one(dic)


class SpiderHamshahri(scrapy.Spider):
    name = "Hamshahrionline_spider"
    allowed_domains = ['hamshahrionline.ir']

    if rss_reader('https://www.hamshahrionline.ir/rss') == 'Success':
        with open("links.json", 'r') as f:
            urls = json.load(f)
    else:
        urls = []


    client = MongoClient()
    db = client['newsdb']
    articles = db.articles
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

        title = response.xpath('//h1[@class="title"]/a/text()').get()
        dic["title"] = title

        news_url = response.css('h1[class=title] a::attr(href)').extract()
        if len(news_url)>0:
            news_url = news_url[0]
        dic["url"] = "https://www.hamshahrionline.ir"+news_url

        sections = response.xpath('//li[@class="breadcrumb-item"]/a/text()').getall()
        dic["article_section"] = sections[1:]

        summary = response.xpath('//p[@class="introtext"]/text()').get()
        dic["summary"] = summary

        date = response.xpath('//div[@class="col-6 col-sm-4 col-xl-4 item-date"]/span/text()').get()
        list = date.split(' ')
        # print(list)
        day = convert_persian_to_english_numbers(list[1])
        month = month_dic[list[2]]
        year = convert_persian_to_english_numbers(list[3])
        jalili_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        time = list[5]
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

        code = response.xpath('//div[@class="item-code"]/span/text()').get()
        dic["code"] = code

        tags = response.xpath('//section[@class="box tags"]/div/ul/li/a/text()').getall()
        dic["tags"] = tags

        text_parts = response.xpath('//div[@class="item-text"]/p/text()').getall()

        text = ""
        for text_part in text_parts:
            text += text_part;

        dic["text"] = text

        client = MongoClient()
        db = client['newsdb']
        articles = db.articles
        result = articles.insert_one(dic)

class KhabarOnlineSpider(scrapy.Spider):
    name = "khabarOnline_spider"
    allowed_domains = ['khabaronline.ir']

    if rss_reader('https://www.khabaronline.ir/rss') == 'Success':
        with open("links.json", 'r') as f:
            urls = json.load(f)
    else:
        urls = []


    client = MongoClient()
    db = client['newsdb']
    articles = db.articles
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
        dic = {"timestamp":"", "url" : " " , "date" : " ", "text" : " ", "summary" : " " , "tags": [] , "article_section" : " ", "code" : " "}

        news_url = response.xpath('//meta[@name="twitter:url"]').xpath('@content').get()
        dic["url"] = news_url

        article_section = response.xpath('//meta[@property="article:section"]').xpath('@content').getall()
        dic["article_section"] = article_section


        item_summary_SELECTOR = '.item-summary p ::text'
        if (response.css(item_summary_SELECTOR).extract()) :
            dic["summary"] = response.css(item_summary_SELECTOR).extract()[0]

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

        client = MongoClient()
        db = client['newsdb']
        articles = db.articles
        result = articles.insert_one(dic)


class SpiderSobhane(scrapy.Spider):
    name = "Sobhane_spider"
    allowed_domains = ['sobhanehonline.com']

    if rss_reader('http://sobhanehonline.com/fa/rss/allnews') == 'Success':
        with open("links.json", 'r') as f:
            urls = json.load(f)
    else:
        urls = []


    client = MongoClient()
    db = client['newsdb']
    articles = db.articles
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


        dic = {"timestamp": "", "url": " ", "date": " ", "text": " ", "summary": " ", "tags": [], "article_section": " ", "code": " "}


        news_url = response.css('h1[class=title] a::attr(href)').extract()
        if len(news_url)>0:
            news_url = news_url[0]
        dic["url"] = "http://sobhanehonline.com"+news_url

        sections = response.xpath('//div[@class="news_path"]/a/text()').getall()
        if len(sections) > 0:
            dic["article_section"] = sections[0]

        summary = response.xpath('//div[@class="subtitle"]/text()').get()
        dic["summary"] = summary

        date = response.xpath('//div[@class="news_nav news_pdate_c"]/text()').get()
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

        code = response.xpath('//div[@class="news_nav news_id_c"]/text()').get()
        dic["code"] = code

        tags = response.xpath('//a[@class="tags_item"]/text()').getall()
        dic["tags"] = tags

        text_parts = response.xpath('//div[@align="justify"]/text()').getall()

        text = ""
        for text_part in text_parts:
            text += text_part;

        if (len(text)<1):
            maybe_text = response.xpath('//div[@class="body"]/text()').getall()
            for t in maybe_text:
                text += t
            maybe_p = response.xpath('//div[@class="body"]/p/text()').getall()
            for p in maybe_p:
                text += p

        dic["text"] = text

        client = MongoClient()
        db = client['newsdb']
        articles = db.articles
        result = articles.insert_one(dic)

# configure_logging()
# runner = CrawlerRunner()

# @defer.inlineCallbacks
# def crawl():
#     yield print(datetime.datetime.now())
#     yield print("asriran started")
#     yield runner.crawl(SpiderAsriran)
#     yield print(datetime.datetime.now())
#     yield print("asriran finished , YJC started")
#     yield runner.crawl(YJCSpider)
#     yield print(datetime.datetime.now())
#     yield print("YJC finished , hamshahri started")
#     yield runner.crawl(SpiderHamshahri)
#     yield print(datetime.datetime.now())
#     yield print("hamshahri finished , khabaronline started")
#     yield runner.crawl(KhabarOnlineSpider)
#     yield print(datetime.datetime.now())
#     yield print("khabaronline finished , sobhane started")
#     yield runner.crawl(SpiderSobhane)
#     yield print(datetime.datetime.now())
#     yield print("sobhane finished")
#     reactor.stop()

# crawl()
# reactor.run()