"""
    https://github.com/rockyzhengwu/FoolNLTKhttps://github.com/rockyzhengwu/FoolNLTK
"""
import q
from pyhanlp import HanLP, JClass

with open("../test_data/1.txt", "r") as rf:
    text = rf.read()

text = text[:502]

import fool

result = fool.cut(text)

print(" ".join(result[0]))


import fool

words, ners = fool.analysis(text)
print(ners)
"""
[[
    (0, 5, 'company', '新浪科技'),
    (6, 9, 'location', '北京'),
    (10, 18, 'time', '4月29日晚间'),
    (20, 25, 'company', '搜狗公司'),
    (24, 27, 'time', '今天'),
    (31, 37, 'time', '3月31日'),
    (37, 47, 'time', '2019年第一季度'),
    (60, 65, 'time', '第一季度'),
    (91, 94, 'location', '美国'),
    (108, 113, 'time', '第一季度'),
    (132, 135, 'time', '去年'),
    (150, 153, 'location', '美国'),
    (171, 176, 'time', '第一季度'),
    (197, 200, 'company', '搜狗'),
    (199, 203, 'job', 'CEO'),
    (202, 206, 'person', '王小川'),
    (206, 210, 'job', 'CFO'),
    (209, 212, 'person', '周毅'),
    (243, 247, 'job', '分析师'),
    (273, 280, 'company', '\n\n高盛银行'),
    (286, 289, 'person', '王总'),
    (302, 306, 'time', '两三年'),
    (386, 389, 'time', '今年'),
    (400, 403, 'person', '王总'),
    (435, 439, 'time', '两三年'),
    (489, 493, 'person', '王小川')
]]

"""