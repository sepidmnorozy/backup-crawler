from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
e1 = {
    "first_name":"nitin",
    "last_name":"panwar",
    "age": 27,
    "about": "Love to play cricket",
    "interests": ['sports','music'],
}
# res = es.index(index='megacorp', doc_type='employee', id=1, body=e1)
# res=es.get(index='megacorp',doc_type='employee',id=1)
# print(res)
e2={
    "first_name" :  "Jane",
    "last_name" :   "Smith",
    "age" :         32,
    "about" :       "I like to collect rock albums",
    "interests":  [ "music" ]
}
e3={
    "first_name" :  "Douglas",
    "last_name" :   "Fir",
    "age" :         35,
    "about":        "I like to build cabinets",
    "interests":  [ "forestry" ]
}
# res=es.index(index='megacorp',doc_type='employee',id=2,body=e2)
# print(res)
# res=es.index(index='megacorp',doc_type='employee',id=3,body=e3)
# print(res)


e4={
    "first_name" :  "سپیده",
    "last_name" :   "ملانوروزی",
    "age" :         23,
    "about":        "به درد خبرها هم میخوره یا نه ؟",
    "interests":  [ "پردازش زبان طبیعی" ]
}
# res=es.index(index='megacorp',doc_type='employee',body=e4)
# print(res)

# res= es.search(index='randomindex', doc_type='document', body={'query':{'match_all':{}}})
res= es.search(index='newsindex', doc_type='news', body={'query':{'match_all':{}}})
# res= es.search(index='megacorp',body={'query':{'match':{'first_name':'ni'}}})
# res= es.search(index='megacorp',doc_type='employee',body={
#         'query':{
#             'match_phrase':{
#                 "about":"خبرها"
#             }
#         }
#     })
print('Got %d hits:' %res['hits']['total']['value'])
# print(res)