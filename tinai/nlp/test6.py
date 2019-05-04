"""
https://github.com/lancopku/pkuseg-python
"""

import q
from pyhanlp import HanLP, JClass

with open("../test_data/1.txt", "r") as rf:
    text = rf.read()

text = text[:502]

import pkuseg

seg = pkuseg.pkuseg()           # 以默认配置加载模型
text = seg.cut(text)  # 进行分词
print(" ".join(text))
