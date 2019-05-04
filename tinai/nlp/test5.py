"""
https://github.com/isnowfy/snownlp
"""

import q
from pyhanlp import HanLP, JClass

with open("../test_data/1.txt", "r") as rf:
    text = rf.read()

text = text[:502]

from snownlp import SnowNLP

s = SnowNLP(text)

print(" ".join(list(s.words)))
