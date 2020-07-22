import math
def make_six_digit_num(input):
    six = input/(100000)
    five = input/(10000)
    four = input / (1000)
    three = input / (100)
    if six > 1 :
        return str(input)
    elif five > 1 :
        return '0'+str(input)
    elif four > 1 :
        return '00'+str(input)
    elif three > 1 :
        return '000'+str(input)
    else:
        return '000102'



import datetime
print(datetime.datetime.now())
num_of_docs = 0
words_occur = {}
count = 0
for i in range(102, 991230):
    filename = "../crawler_Datas/corpus/HAM2-" + make_six_digit_num(i) + ".xml"

    try:
        f = open(filename, "r")
        count += 1
        lines = f.readlines()
        #each line is a document
        num_of_docs += len(lines)
        for line in lines:
            # each line is a document
            list = line.split("@@@@@@@@@@ ")
            document = list[1]
            # add words to corpus words
            doc_words = document.split(" ")
            myset = set(doc_words)
            for word in myset:
                if word in words_occur:
                    words_occur[word] += 1
                else:
                    words_occur[word] = 1

    except FileNotFoundError:
        # print("num of seen files : "+str(count))
        continue



print("lalala")
print(num_of_docs)


for word in words_occur:
    words_occur[word] = math.log(num_of_docs/words_occur[word],2)

print("haha")
# idf_dic = {}

# print(len(words_in_corpus))
# for word in words_in_corpus:
#     num_of_docs_with_t = num_of_ducuments_that_have_t(word, documents_in_corpus)
#     idf = math.log10(num_of_docs/num_of_docs_with_t)
#     idf_dic[word] = idf

print("lele")
import operator
sorted_x = sorted(words_occur.items(), key=operator.itemgetter(1))

import collections
sorted_dict = collections.OrderedDict(sorted_x)

print("lolo")

final_res = {"res": sorted_x}

import json
with open('res.json', 'w') as json_file:
    json.dump(final_res, json_file)


