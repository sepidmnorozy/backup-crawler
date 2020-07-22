from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
e1 = {"first":"nitin", "age":[1, 0, 1, 0, 1]}
e2 = {"first":"sepid", "age":[0, 1, 1, 1, 0]}
e3 = {"first":"mamad", "age":[0, 1, 0, 1, 0]}
#es.index(index='test', doc_type='test', body=e1)
#es.index(index='test', doc_type='test', body=e2)
#es.index(index='test', doc_type='test', body=e3)
#res=es.get(index='megacorp',doc_type='employee',id=1)
#res= es.search(index='test', doc_type='test', body={"query": {"match":{"age":[1,1,1,1,1]}}})
res = es.delete(index='test', body={"query":{"match":{}}})
print(res)
#print('Got %d hits' %res['hits']['total']['value'])
