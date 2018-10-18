#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import math


reload(sys).setdefaultencoding("utf8")


doc_content = {
    "拒接": [
        "您好！您拨叫的用户暂时无人接听，请您稍后再拨。",
        "您好！您拨叫的用户暂时无法接听电话，如需留言，请按一，留言，将收取正常通话费用。",
        "您拨打的用户已开通中国移动来电提醒业务，我们将短信通知机主您的来电，本次通话免费。",
        "您拨打的用户已开通天翼通信助理服务，语音留言请按一，人工服务请按二，感谢通知请挂机。",
    ],
    "正忙": [
        "您好！您拨叫的用户正忙，请您稍后再拨。",
        "您拨叫的用户正忙，请您稍后再拨。",
        "用户忙，请稍后再拨。",
        "您好！您拨叫的用户正在通话中，请稍后再拨。"
    ],
    "关机": [
        "您拨打的用户不在服务区或已关机，如需留言请按一，留言将收取正常通话费用。",
        "您好，您拨打的电话已关机。",
        "您好，您拨叫的用户已关机，请您稍后再拨。",
        "您好，四川移动来电提醒业务，为您服务。您所拨打的用户已关机，我们将尽快用短信通知对方。本次通话免费，谢谢，请挂机。"
    ],
    "停机": ["您好！您拨叫的用户已停机。"],
    "空号": ["您好，您拨打的号码是空号，请核对后再拨。"],
    "无法接通": ["您好，您拨叫的用户暂时无法接通，请稍后再拨。"],
    "外呼暂停服务": ["您好，您的手机号码已被暂停服务。"],
    "外呼欠费停机": ["您好，您的手机号码已欠费停机。"]
}

target_doc = [
    "您的手机号码已暂停服务。",
    "用户忙，请稍后再拨。",
    "大象大象大象大象大象大象大象用户忙大象",
    "大象大象大象大象大象大象大象用户忙大象稍后大象再拨",
    "文章中出现次数最多的词的出现次数",
    "大象大象大象大象大象大象大象大象大象大象大象关机",
    "大象大象大象大象大象大象大象大象大象大象大象提醒",
]


# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
dic_main = {"拨打", "短信", "业务", "提醒", "稍后", "接听电话", "语音", "暂时", "为您服务", "无法", "服务区", "人工", "服务", "正在", "收取", "用户", "助理", "不在", "用户忙", "来电", "欠费", "暂停", "正常", "费用", "核对", "拨叫", "通话中", "留言", "接通", "通知", "本次", "人工服务", "关机", "来电提醒", "停机", "正忙", "无人接听", "电话", "核对后", "无人", "对方", "再拨", "空号", "号码", "开通", "接听", "请按", "通话", "免费", "机主", "挂机"}


# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# 1. 词袋模型 -> 提取分词,计算词频 + 记录所有的词
doc2word_list = []
doc2word_map = []
all_word = []

for key in doc_content:
    doc_list = doc_content[key]
    for doc in doc_list:
        doc2word_list.append({})
        doc2word_map.append(key)
        for word in dic_main:
            if word in doc:
                doc2word_list[-1][word] = doc.count(word)
                if word not in all_word:
                    all_word.append(word)

print "\r\ndoc2word_list:"
for item in doc2word_list:
    print str(item).decode("string_escape")

print "\r\ndoc2word_map:"
for item in doc2word_map:
    print item,

print "\r\n\r\nall_word:"
for word in all_word:
    print word,
print


# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# 2. 获取词频向量。获取 文章中出现次数最多的词的出现次数
doc2word2vector_list = []
max_appear_list = []
for wordlist in doc2word_list:
    doc2word2vector_list.append([])
    maxc = 1
    for word in all_word:
        doc2word2vector_list[-1].append(wordlist.get(word, 0))
        maxc = max(doc2word2vector_list[-1][-1], maxc)
    max_appear_list.append(maxc)

print "\r\ndoc2word2vector_list:"
for item in doc2word2vector_list:
    print item

print "\r\nmax_appear_list:\r\n", max_appear_list


# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# 3. 计算 TF-IDF
# TF = 某个词出现的次数 / 文章中出现次数最多的词的出现次数
# IDF = log(文档总数 / 包含该词的文档数)
#   - improve：此处【包含该词的文档数】摘除同类下的所有文章，即计算【关机】类时，不计算【关机】类下的其他文章的数量
#   - 从而避免 类内距离 扩散到 类间距离
tfidf_list = []
for i, doc2word in enumerate(doc2word_list):
    maxc = max_appear_list[i]
    tfidf_list.append([])
    for word in all_word:
        tf = 1.0 * doc2word.get(word, 0) / maxc
        jlist = [j for j, x in enumerate(doc2word_list) if word in x]
        jcount = len(jlist)
        for j in jlist:
            if i != j and doc2word_map[i] == doc2word_map[j]:
                jcount -= 1
        idf = math.log(1.0 * len(doc2word_list) / (jcount + 1))
        tfidf_list[-1].append(tf * idf)

print "\r\ntfidf_list:"
for item in tfidf_list:
    print item


# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# 4. 同理获取目标文档的向量

target_doc2word_list = []
target_word2vector_list = []
target_max_appear_list = []

for tdoc in target_doc:
    target_word2vector_list.append([])
    target_doc2word_list.append({})
    maxc = 1
    for word in all_word:
        if word in tdoc:
            target_doc2word_list[-1][word] = tdoc.count(word)
            target_word2vector_list[-1].append(tdoc.count(word))
            maxc = max(target_word2vector_list[-1][-1], maxc)
        else:
            target_word2vector_list[-1].append(0)

    target_max_appear_list.append(maxc)

print "\r\ntarget_doc2word_list:"
for item in target_doc2word_list:
    print str(item).decode("string_escape")

print "\r\ntarget_word2vector_list:"
for item in target_word2vector_list:
    print item

print "\r\ntarget_max_appear_list:\r\n", target_max_appear_list

# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# 5. 计算目标文档的 TF-IDF
# TF = 某个词出现的次数 / 文章中出现次数最多的词的出现次数
# IDF = log(文档总数 / 包含该词的文档数)
target_tfidf_list = []

for i, tword in enumerate(target_word2vector_list):
    target_tfidf_list.append([])
    maxc = target_max_appear_list[i]
    for word in all_word:
        tf = 1.0 * target_doc2word_list[i].get(word, 0) / maxc
        idf = math.log(1.0 * len(doc2word_list) / (1 + len([True for x in doc2word_list if word in x])))
        target_tfidf_list[-1].append(tf * idf)

print "\r\ntarget_tfidf_list:"
for item in target_tfidf_list:
    print item


# ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
# 6. 计算TF-IDF的余弦夹角值

target_sin = []

for target_vector in target_tfidf_list:
    flen = len(target_vector)
    target_sin.append([])
    for doc_vector in tfidf_list:
        x = sum([target_vector[i]*doc_vector[i] for i in xrange(flen)])
        y = math.sqrt(sum([target_vector[i]*target_vector[i] for i in xrange(flen)])) * math.sqrt(sum([doc_vector[i]*doc_vector[i] for i in xrange(flen)]))
        if y == 0:
            target_sin[-1].append(0.0)
        else:
            target_sin[-1].append(1.0 * x / y)

print "\r\ntarget_sin:"
for item in target_sin:
    print sorted(item, reverse=True)

print "\r\nresult:"
for item in target_sin:
    for x, y in sorted(zip(doc2word_map, item), key=lambda x: -x[1]):
        print x, y
    print
