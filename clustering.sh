#!/bin/bash
cd /home/momtazi/Projects/news_tracker/crawler/sepidenv
source bin/activate
#activated venv
cd /home/momtazi/Projects/news_tracker/crawler
python classification.py
python clean_clusters.py
#python clean_w2v_clusters.py
#python clean_tfidf_clusters.py
python save_eval_clusters.py
#ls
