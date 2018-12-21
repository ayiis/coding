#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import traceback
import os
import math
import csv
import re
import random
from langconv import Converter
import jieba.posseg as pseg


# DATA_PATH = os.path.join(os.path.realpath(".."), "data")
DATA_PATH = os.path.join(os.path.realpath("."), "data")


class BaseNlp():
    def __init__(self):
        self._sym_dir = os.path.join(DATA_PATH, "sym_chunk.csv")
        self._tf_dir = os.path.join(DATA_PATH, "tf.txt")
        self._del_dir = os.path.join(DATA_PATH, "del_chunk.csv")
        self._denial_dir = os.path.join(DATA_PATH, "denial_chunk.csv")
        self._sp_dir = os.path.join(DATA_PATH, "skip_chunk.csv")
        self._nbs_dir = os.path.join(DATA_PATH, "zh_nbs.txt")
        self._cut_dir = os.path.join(DATA_PATH, "cut_chunk.csv")

        self._sym_files = [
            os.path.join(DATA_PATH, "syno_from_baidu_hanyu_translation.txt"),
            os.path.join(DATA_PATH, "syno_from_baidu_hanyu.txt"),
            os.path.join(DATA_PATH, "syno_from_cwn.txt"),
            os.path.join(DATA_PATH, "syno_from_hh.txt")
        ]

        self._del_set = set([x[0] for x in self._load_csv(self._del_dir)])
        self._den_set = set([x[0] for x in self._load_csv(self._denial_dir)])
        self._sp_list = set([x[0] for x in self._load_csv(self._sp_dir)])
        self._cut_list = set([x[0] for x in self._load_csv(self._cut_dir)])

    def _load_csv(self, csv_dir):
        with open(csv_dir, "r") as rf:
            return [x for x in csv.reader(rf) if x]


def tradition2simple(line):
    return Converter("zh-hans").convert(line)


def get_comment_data_csv(file_path):
    with open(file_path, "r") as rf:
        return [tradition2simple(x[2].strip().replace("\n", ",").upper()) for i, x in enumerate(csv.reader(rf)) if i > 0]


def get_comment_data_default(file_path):
    with open(file_path, "r") as rf:
        return re.split(r"\r|\n|\||\t", rf.read())


def get_comment_data_html(file_path):
    from pathlib import Path
    all_contents = []
    for path in Path(file_path).glob("*.html"):
        file_name = "%s" % path
        with open(file_name, "r") as rf:
            f_contents = []
            contents = re.split(r"\r|\n|\||\t", rf.read())

        for content in contents:
            if not content:
                continue
            content = tradition2simple(content.strip().replace("\n", ",").upper())
            if not content:
                continue

            if "当前位置：广州妈妈论坛" in content:
                continue

            f_contents.append(content)

        all_contents += f_contents

    return all_contents


def get_comment_data(file_path):
    return get_comment_data_html(file_path)
    # return get_comment_data_csv(file_path)


def chunk_stat(sent_list):
    chunk_dict = {}
    for ent in sent_list:
        chunk_dict[ent] = chunk_dict.get(ent, 0) + 1
    chunk_list = list(chunk_dict.items())
    chunk_list.sort(key=lambda x: -x[1])
    return chunk_list


def str2chunk(sent):
    return [tuple(x) for x in pseg.cut(sent)]


def inner_p(str0, str1):
    return sum([float(x) * float(y) for x, y in zip(str0.split(","), str1.split(","))])


def prepare_nlp_data(comment_list):

    try:
        # build base nlp data
        base_nlp = BaseNlp()

        # cut comment data into sentences
        # cut_list_pattern =
        cut_list_pattern = r"[%s]" % ("".join(base_nlp._cut_list).replace("", "\\")[:-1])
        cut_list = [cut_line for sent in comment_list for cut_line in re.split(cut_list_pattern, sent) if cut_line]
        # out: ['酒店不错', '很现代', '房间很时尚', '地理位置也不错', '不愧是W酒店', '夜店风格', '适合年轻人入住', '下次还会选择W酒店入住', '不错', ...

        # cut into keywords
        seg_cmt = [str2chunk(x) for x in cut_list]
        # out: [[('酒店', 'n'), ('不错', 'a')], [('很', 'zg'), ('现代', 't')], [('房间', 'n'), ('很', 'zg'), ('时尚', 'n')], [('地理位置', 'n'), ('也', 'd'), ('不错', 'a')], ...

        # remove some normal words by dict
        del_set_pattern = base_nlp._del_set | base_nlp._sp_list
        trans_comment = [list(filter(lambda xx: xx[0] not in del_set_pattern, x)) for x in seg_cmt]
        trans_comment = [x for x in trans_comment if x]
        # out: [[('酒店', 'n'), ('不错', 'a')], [('现代', 't')], [('房间', 'n'), ('时尚', 'n')], [('地理位置', 'n'), ('不错', 'a')], [('不愧', 'a'), ('W', 'eng'), ('酒店', 'n')], ...

        # filter only noun
        filt_comment = [list(filter(lambda xx: "n" in xx[1], x)) for x in trans_comment]
        filt_comment = [x for x in filt_comment if x]
        # out: [[('酒店', 'n')], [('房间', 'n'), ('时尚', 'n')], [('地理位置', 'n')], [('W', 'eng'), ('酒店', 'n')], [('夜店', 'n'), ('风格', 'n')], [('年轻人', 'n')], ...

        # get TF
        chunk_dict = {}
        for sent in filt_comment:
            for keyword, _ in sent:
                chunk_dict[keyword] = chunk_dict.get(keyword, 0) + 1
        # out: {'酒店': 35, '房间': 16, '时尚': 4, '地理位置': 3, 'W': 5, '夜店': 1, '风格': 5, '年轻人': 4, '女生': 1, '直发棒': 1, '泳池': 2, '电影': 1, '情怀': 1, '伦敦': 1, ...

        # get top N keyword by TF
        chunk_list = list(chunk_dict.items())
        chunk_list.sort(key=lambda x: -x[1])
        sel_chunk = set([x[0] for x in chunk_list[:200]])
        # out: {'年轻人', '服务质量', '布置', '出口', '门市价', '处', '服务', '窗帘', '热情', '客人', '价', '几楼', '有点', '安静', '电梯间', '气氛', '夜店', ...

        # get TF-IDF: word and value:
        with open(base_nlp._nbs_dir, "r") as rf:
            nb_item = [tuple(x.strip().split(" ")[:2]) for x in rf.readlines()]

        nb_dict = dict(nb_item)
        # out: <all of the dict>
        sel_nb = set(list(filter(lambda x: x[0] in sel_chunk, nb_item)))
        # out: [('公用', '0.0320,0.0921,-0.1031,-0'), ('年轻人', '0.0021,0.0022,-0.2474,0.'), ('酒吧', '-0.1038,-0.0226,-0.0772,'), ('热情', '0.1083,0.0889,0.0078,-0.'), ...

        return {
            "sel_chunk": sel_chunk,
            "chunk_dict": chunk_dict,
            "nb_dict": nb_dict,
            "sel_nb": sel_nb,
            "trans_comment": trans_comment,
        }
    except Exception:
        print(traceback.format_exc())


def analyze_input(user_ask):
    user_ask = tradition2simple(user_ask.strip().replace("\n", "").upper())
    print("user_ask:", user_ask)

    # if user_ask in ["全部评价", "所有评价", "所有", "全部", "尚品宅配怎么样"]:
    #     return ["全部"]
    # else:

    result = [tuple(x) for x in pseg.cut(user_ask)]
    print("pseg.result:", result)
    result = [x[0] for x in result if x[1][0] == "n"]
    print("user_ask:", user_ask)
    return result


def do_answer(nlp_data, user_ask):

    prefix_format = ["少数", "有些", "一些", "一部分", "部分", "相当一部分", "很多", "大部分", "多数", "大多数", "非常多", "极多"]
    normal_answer_format = [
        """%s网友觉得%s %s""",
        """%s网友给%s的评价是 %s""",
        """%s网友给%s的印象是 %s""",
        """%s网友给%s的感觉是 %s""",
        """%s网友认为%s %s""",
        """%s网友说%s %s""",
    ]
    empty_answer_format = [
        """网友们没有对 %s 发表意见""",
        """网友们对 %s 没有印象""",
        """网友们很少讨论 %s""",
    ]
    empty_answer = [
        """网友们似乎没有对这个话题发表意见。""",
        """网友们似乎对这个话题没有印象。""",
        """网友们似乎很少讨论这个话题。""",
        """网友们似乎不关心这个话题。""",
        """网友们似乎没聊过相关话题。""",
    ]

    try:
        user_ask_list = analyze_input(user_ask)
        # user_ask_list = "交通 环境 床".split(" ")
        # user_ask_list = "回升".split(" ")
        # user_ask_list = "床 床头柜".split(" ")
        print("user_ask_list:", user_ask_list)
        if "全部" in user_ask_list:
            use_chunk = [(x, "n") for x in nlp_data["sel_chunk"]]
        else:
            seg_list = [str2chunk(sent) for sent in user_ask_list]
            use_chunk = []
            for seg_sent in seg_list:
                use_chunk.extend(seg_sent)

        print("use_chunk:", use_chunk)
        # out: [('交通', 'n'), ('环境', 'n'), ('床', 'n'), ...

        hold_chunk = {}
        for keyword, clss in use_chunk:
            use_keyword = None
            if keyword in nlp_data["chunk_dict"]:
                use_keyword = keyword
            elif keyword in nlp_data["nb_dict"]:
                # get the max distance of each keyword between the INPUT and the EXISTS
                max_p = 0
                for x, p in nlp_data["sel_nb"]:
                    distance = inner_p(p, nlp_data["nb_dict"][keyword])
                    # out: [('环境', -0.08543105), ('一楼', -0.004940900000000001), ('交通', 0.018205909999999995), ('一流', 0.01749487999999998), ('印象', -0.060714080000000024), ...
                    if distance > max_p:
                        max_p, use_keyword = distance, x
                print("use_keyword:", use_keyword, max_p)

            if not use_keyword:
                print("Cannot parse chunk: ", keyword)
                continue

            # get all sentences that contains the `use_keyword`
            filt_seg = list(filter(lambda x: next((True for xx in x if use_keyword == xx[0]), False), nlp_data["trans_comment"]))
            # print("filt_seg:", filt_seg)
            # out: [[('酒店', 'n'), ('环境', 'n'), ('不错', 'a')], [('酒店', 'n'), ('环境', 'n'), ('不错', 'a')], [('环境', 'n'), ('不错', 'a')], ...

            # get the adjective word of it
            filt_chunk = [y[0] for x in filt_seg for y in x if y[1] == "a"]   # ["a", "t"]
            # out: ['不错', '不错', '不错', '好', '不错', '不错', '好', '好', '好', '不错', '不错', '不错', '奢华', '方便', '不错', ...

            # print("filt_chunk:", filt_chunk)
            ch_stat = chunk_stat(filt_chunk)
            # print("ch_stat:", ch_stat)
            # ch_stat_dict = dict(ch_stat)
            # print("ch_stat_dict:", ch_stat_dict)

            # tmp_list = list(filter(lambda x: x[1] >= 2 and x[0] != keyword, ch_stat))
            # if tmp_list:
            #     hold_chunk[keyword] = tmp_list

            hold_chunk[keyword] = list(filter(lambda x: x[1] >= 2 and x[0] != keyword, ch_stat))
            # hold_chunk[keyword].append((keyword, max([ch_stat_dict.get(keyword, 10), ch_stat_dict.get(use_keyword, 10)])))

        print("** hold_chunk:", hold_chunk)
        # out: {'电视柜': [('简单', 6), ('小', 5), ('好', 4), ('短', 4), ('最好', 3), ('一般', 3), ('后来', 2), ('深', 2), ('大', 2), ('完整', 2), ...

        if hold_chunk:

            # cut the items
            # at least 6 ( or all ), at most 10% of all comment
            for key in hold_chunk:
                hold_chunk[key] = hold_chunk[key][:max(int(len(hold_chunk[key]) / 10), 6)]

            sum_each = {key: sum([y[1] for y in hold_chunk[key]]) for key in hold_chunk}
            print("sum_each:", sum_each)

            r_population = []
            r_weights = []

            for key in sum_each:
                r_population.append(key)
                r_weights.append(sum_each[key])

            answer_keyword = random.choices(population=r_population, weights=r_weights)
            print("answer_keyword:", answer_keyword)
            answer_keyword = answer_keyword[0]

            r_weights = [x[1] for x in hold_chunk[answer_keyword]]

            answer_comment = random.sample(hold_chunk[answer_keyword], min(len(hold_chunk[answer_keyword]), 1))
            print("answer_comment:", answer_comment)
            if not answer_comment:
                return random.choice(empty_answer)

            answer_comment_text = ",".join([x[0] for x in answer_comment])
            answer_comment_weight = sum([x[1] for x in answer_comment])
            print("answer_comment_weight:", answer_comment_weight)

            percent = 100 * answer_comment_weight / sum_each[answer_keyword]
            answer_format = random.choice(normal_answer_format)

            percent_align = percent * len(prefix_format) / 30.0
            p1, p2 = max(int(percent_align) - 2, 0), min(math.ceil(percent_align) + 2, len(prefix_format))
            p1 = min(p1, p2 - 1)
            print("p1: p2:", p1, p2)
            print("prefix_format:", prefix_format[p1: p2])
            prefix = random.choice(prefix_format[p1: p2])

            # return answer_format % (prefix, percent, answer_comment_text)
            return answer_format % (prefix, "", answer_comment_text)
            # return answer_format % (int(100 * answer_comment_weight / sum_each[answer_keyword]), answer_keyword, answer_comment_text)

        else:
            return random.choice(empty_answer)

        # DONE IT NOW

        sum_each = {key: sum([y[1] for y in hold_chunk[key]]) for key in hold_chunk}
        print("sum_each:", sum_each)

        for key, comment in hold_chunk.items():
            if comment:
                answer_format = random.choice(normal_answer_format)
                return answer_format % (key, ", ".join(["%s%s" % (x[1], x[0]) for x in comment if x]))
            else:
                answer_format = random.choice(empty_answer_format)
                return answer_format % (key)

        return random.choice(empty_answer)
        # DONE IT NOW

        ask_list = ",".join(list(hold_chunk.keys())[:6])
        if len(hold_chunk.keys()) > 6:
            ask_list += "..."

        answer_dict = {}
        for y in hold_chunk.values():
            for x0, x1 in y:
                answer_dict[x0] = answer_dict.get(x0, 0) + x1
        answer_list = ", ".join(["%s%s" % (x[1], x[0]) for x in answer_dict.items()])
        # print("hold_chunk.values():", list(hold_chunk.values()))
        # answer_list = ",".join(["%s%s" % (x[1], x[0]) for y in hold_chunk.values() for x in y if x])

        if answer_list:
            print(normal_answer_format % (ask_list, answer_list))

    except Exception:
        print(traceback.format_exc())

    return random.choice(empty_answer)


def main():
    import pickle

    # file_path = "/home/ayiis/comment_anals/w_hotel.csv"
    file_path = "/home/ayiis/comment_anals/text_mamacn"
    comment_list = get_comment_data(file_path)
    nlp_data = prepare_nlp_data(comment_list)

    with open("data/spzp.pkl", "wb") as wf:
        pickle.dump(nlp_data, wf)

    with open("data/spzp.pkl", "rb") as rf:
        nlp_data = pickle.load(rf)

    print("File load complete.")

    while True:
        user_ask = input("What do you want to know?: ")
        ai_answer = do_answer(nlp_data, user_ask)
        print("ai:", ai_answer)


if __name__ == "__main__":
    main()
