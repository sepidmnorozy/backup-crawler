import scrapy
import jdatetime
import datetime
from my_crawler_nums import convert_persian_to_english_numbers, num_dic, month_dic


class KhabarOnlineSpider(scrapy.Spider):
    name = "khabarOnline_spider"
    allowed_domains = ['khabaronline.ir']

    start_urls = ['https://www.khabaronline.ir/news/1317901/%DA%86%D9%87%D8%B1%D9%87-%D9%86%D8%B2%D8%AF%DB%8C%DA%A9-%D8%A8%D9%87-%D9%82%D8%A7%D9%84%DB%8C%D8%A8%D8%A7%D9%81-%D8%B3%D8%AE%D9%86%DA%AF%D9%88%DB%8C-%D8%B4%D9%88%D8%B1%D8%A7%DB%8C-%D9%88%D8%AD%D8%AF%D8%AA-%D8%B4%D8%AF']

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
        print("******************************************************************************")
        print(date)
        if date == None:
            print("eeeeeeeeeeee")
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
