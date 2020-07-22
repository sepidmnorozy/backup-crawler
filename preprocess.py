def preprocess(txt):
    res = ''
    if txt is not None and len(txt) > 1:
        punc_list = ["؟", "?", "!", ".", "،", ","]

        for punc in punc_list:
            txt_list = [s.replace(punc, "") for s in txt]
            res = ''.join(txt_list)

    return txt