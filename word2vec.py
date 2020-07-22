import regex
import numpy as np

f=open("/home/momtazi/Projects/news_tracker/crawler/twitt_wiki_ham_blog.fa.text.100.vec", "r")
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

def get_word2vec(a):
    text = ""

    if "preprocessed_summary" in a:
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
    # newString = (processed_text.encode('ascii', 'ignore')).decode("utf-8")
    tokens = regex.findall(r'\p{Letter}+', processed_text)
    vector = np.zeros(100)
    if len(tokens) > 0:
        for token in tokens:
            if token in words_list:
                token_vector = vectors_list[words_list.index(token)]
                vector += token_vector
        vector = vector/len(tokens)

    return vector