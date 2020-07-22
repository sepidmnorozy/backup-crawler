import requests
from requests.exceptions import HTTPError
import xml.etree.ElementTree as ET
import json

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


#print(rss_reader('https://namehnews.com/fa/rss/allnews'))
