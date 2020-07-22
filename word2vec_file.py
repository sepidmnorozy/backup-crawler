import numpy as np



f=open("../crawler_Datas/twitt_wiki_ham_blog.fa.text.100.vec", "r")
lines = f.readlines()

words_list = []
vectors_list = []

for i in range(1, len(lines)):
    # print("***********")
    line_tokens = lines[i].split(" ")
    word_vector = np.zeros(100)
    word = line_tokens[0]
    words_list.append(word)

    for j in range(1, 101):
        if j == 100:
            word_vector[j - 1] = line_tokens[j].replace("\n", "")
        else:
            word_vector[j - 1] = line_tokens[j]

    vectors_list.append(word_vector)

#     # if i == 2 :
#     #     print(word)
#     #     print(word_vector)
#
#
# client = MongoClient()
# db = client['newsdb_preprocess']
#
# articles = db.articles
#
#
# vector = np.zeros(100)
#
# doc_vec = []
#
# print("haha")
# for a in articles.find():
#     text = ""
#     if a["title"] is not None:
#         if len(a["title"]) > 1:
#             text += a["title"] + " "
#
#     if a["text"] is not None:
#         if len(a["text"]) > 1:
#             text += a["text"]
#
#
#     processed_text = " ".join(text.split())
#     # newString = (processed_text.encode('ascii', 'ignore')).decode("utf-8")
#     tokens = regex.findall(r'\p{Letter}+', processed_text)
#     if len(tokens) > 0 :
#         vector = np.zeros(100)
#         for token in tokens:
#             if token in words_list:
#                 token_vector = vectors_list[words_list.index(token)]
#                 vector += token_vector
#         list = [text, vector]
#         doc_vec.append(list)
#
# print("hehe")
# result = []
#
# def similarity(vec, other_vec):
#     dot = np.dot(vec, other_vec)
#     norma = np.linalg.norm(vec)
#     normb = np.linalg.norm(other_vec)
#     cos = dot / (norma * normb)
#     return cos
#
# for list in doc_vec:
#     doc = list[0]
#     vec = list[1]
#
#     similar_docs=[]
#     similar_docs.append(doc)
#
#     for i in range(doc_vec.index(list)+1, len(doc_vec)):
#         other_doc = doc_vec[i][0]
#         other_vec = doc_vec[i][1]
#
#         if (similarity(vec, other_vec) > 0.9):
#             similar_docs.append(other_doc)
#
#     result.append(similar_docs)
#
#
#
# client1 = MongoClient()
# db1 = client1['newsdb']
# similars = db1.similars
# x = similars.delete_many({})
#
#
# count = 0
# for a in similars.find():
#     count +=1
# print(count)
#
#
#
# for res in result:
#     dic = {"text": "", "similar_texts": []}
#     dic["text"] = res[0]
#     similar_texts = []
#     for i in range(1, len(res)):
#         similar_texts.append(res[i])
#     dic["similar_texts"] = similar_texts
#     similars.insert_one(dic)
#
#
# count = 0
# for a in similars.find():
#     count +=1
# print(count)