from elasticsearch import Elasticsearch
es = Elasticsearch()

res = es.delete_by_query(index="newsindex", body={"query": {"match_phrase": {"url": "http://roozno.com"}}})
print(res)
