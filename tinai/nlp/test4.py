"""
https://github.com/fxsjy/jieba
"""

import q
from pyhanlp import HanLP, JClass

with open("../test_data/1.txt", "r") as rf:
    text = rf.read()

text = text[:502]

import jieba

seg_list = jieba.cut(text, cut_all=False, HMM=False)

print(" ".join(list(seg_list)))
