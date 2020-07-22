#!/bin/bash
#scrapy runspider spider1.py
#scrapy runspider spider2.py
#scrapy runspider spider3.py
#scrapy runspider spider4.py
#scrapy runspider spider5.py
#scrapy runspider spider6.py
#scrapy runspider spider7.py
#scrapy runspider spider8.py
#scrapy runspider spider9.py
#scrapy runspider spider10.py
#scrapy runspider spider11.py
#scrapy runspider spider12.py
#scrapy runspider spider13.py
#scrapy runspider spider14.py

cd /home/momtazi/Projects/news_tracker/crawler/sepidenv
source bin/activate
cd /home/momtazi/Projects/news_tracker/crawler
counter=1
while [ $counter -le 22 ]
do
  scrapy runspider spider${counter}.py
  ((counter++))
done
#scrapy runspider spider4.py

