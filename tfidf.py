import json
import regex
import numpy as np
stop_file = open("/home/momtazi/Projects/news_tracker/crawler/PersianStopWordsList.txt", "r")
lines = stop_file.readlines()

stop_words = []

for i in range(1, len(lines)):
    stop_words.append(lines[i].split("\n")[0])

data = []
with open("/home/momtazi/Projects/news_tracker/crawler/res.json", 'r') as f:
    data = json.load(f)

vocab_idf_list = data["res"][0:10000]

vocab_idf_dic = {}

# print(len(vocab_idf_list))
vocab = []

for element in vocab_idf_list:
    v = str(element[0])
    idf = element[1]
    # print(v)
    if v in stop_words:
        continue
    else:
        vocab.append(v)
        vocab_idf_dic[v] = idf

def get_tfidt_vector(a):
    text = ""
    if "preprocessed_summary"in a:
        if a["preprocessed_summary"] is not None:
            if len(a["preprocessed_summary"]) > 1:
                text += a["preprocessed_summary"] + " "

    if "preprocessed_title" in a:
        if a["preprocessed_title"] is not None:
            if len(a["preprocessed_title"]) > 1:
                text += a["preprocessed_title"] + " "

    if "preprocessed_text" in a:
        if a["preprocessed_text"] is not None:
            if len(a["preprocessed_text"]) > 1:
                text += a["preprocessed_text"]

    processed_text = " ".join(text.split())
    tokens = regex.findall(r'\p{Letter}+', processed_text)
    vector = np.zeros(len(vocab))
    # print("this is from idf")
    if len(tokens) > 0:
        for i in range(0, len(vocab)):
            v = vocab[i]
            count = 0
            for token in tokens:
                if token == v:
                    count += 1
            vector[i] = count*vocab_idf_dic[v]
    # if np.all(vector==0):
    #     continue
    # else:
    return vector
