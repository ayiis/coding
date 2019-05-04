"""
https://github.com/thunlp/THULAC-Python
"""

import q
from pyhanlp import HanLP, JClass

with open("../test_data/1.txt", "r") as rf:
    text = rf.read()

text = text[:502]

import thulac

thu1 = thulac.thulac(seg_only=True)  #默认模式
text = thu1.cut(text, text=True)  #进行一句话分词
print(text)