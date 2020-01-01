"""
    -  火龙解压所有
    1. 搜索所有需要翻译的文件
    2. 搜索所有需要翻译的字符串的位置
    3. 使用 set 计算压缩字符串数量
    4. 调用翻译接口获得中文
    5. <确认步骤> 是否
    6. 替换原来的文件的字符串
    -  火龙替换文件
"""
import q
import os
import re
import shutil
import traceback
from pathlib import Path
import time
import configparser
import translation_tool
from lib.w_war3mapskin import (
    Worker as War3mapskinWorker,
)
from lib.w_war3map_wts import (
    Worker as War3mapWtsWorker,
)
from lib.w_war3map_j import (
    Worker as War3mapJWorker,
)
from lib.w_common_ini import (
    AbilityWorker,
    BuffWorker,
    DestructableWorker,
    DoodadWorker,
    ItemWorker,
    UnitWorker,
    UpgradeWorker,
    W3iWorker,
    CommandStringsWorker,
)

ini_work_files = {
    # "table/ability.2.ini": AbilityWorker,

    "map/war3mapskin.txt": War3mapskinWorker,

    "table/unit.ini": UnitWorker,
    "table/ability.ini": AbilityWorker,
    "table/buff.ini": BuffWorker,
    "table/destructable.ini": DestructableWorker,
    "table/doodad.ini": DoodadWorker,
    "table/item.ini": ItemWorker,
    "table/upgrade.ini": UpgradeWorker,

    "table/w3i.ini": W3iWorker,

    "map/Units/CommandStrings.txt": CommandStringsWorker,
}

slk_work_files = {

}

wts_work_files = {
    "map/war3map.wts": War3mapWtsWorker,
}

jass_work_files = {
    # "map/scripts/wj.2.j": War3mapJWorker,

    "map/war3map.j": War3mapJWorker,
    "map/scripts/war3map.j": War3mapJWorker,
}


def qq():
    print("".join(traceback.format_stack()))


class BaseWorker(object):
    """docstring for BaseWorker"""
    def __init__(self):
        super(BaseWorker, self).__init__()

    def write_raw_string(self, wf, line):
        wf.write(line)

    def do_translate(self, translater, from_lan, to_lan):

        try:
            self.trans_result = {}
            fy = translation_tool.init_fanyi(translater, from_lan, to_lan)
            # fy_vi = translation_tool.init_fanyi(translater, "vi", to_lan)
            for sentence in self.sentence_set:

                # 多加try保平安
                try:
                    # if re.match(r'^[a-zA-Z\ _]*$', sentence):
                    res = fy.translate(sentence)
                    # else:
                    #     res = fy_vi.translate(sentence)
                    self.trans_result[sentence] = res
                except Exception:
                    print(traceback.format_exc())

            # print("self.trans_result:", self.trans_result)
        except Exception:
            print(traceback.format_exc())
            pass

        finally:
            fy.save_result()
            # fy_vi.save_result()

    def take_string_from_sentense(self, sentence):
        # 包含 + - % 0-9 因为只是数字不同的技能实在太多了 %s %z %d %c
        temp = re.sub(r"(\-[a-z0-9]+|http[s]?\:\/\/[^\ \"\'\|]+|\<[a-z0-9]{4},[a-z0-9]+\>|TRIGSTR_[0-9]+|\%[a-z]\b|\|c[0-9a-f]{8}|[0-9\+\-\%]|\|n|\|r|[\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\:\"\,\.\/\<\>\?“”])", "*", sentence, flags=re.I)
        # # 除外 + - % 0-9
        # temp = re.sub(r"(\|c[0-9a-f]{8}|\|n|\|r|[\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?])", "*", sentence, flags=re.I)
        # print("sentence:", sentence)
        for string in temp.split("*"):
            string = string.strip()
            if string:
                # 中文和标点符号就放过了吧，老铁
                if re.match(r"^[\u4e00-\u9fa5\u3002|\uff1f|\uff01|\uff0c|\u3001|\uff1b|\uff1a|\u201c|\u201d|\u2018|\u2019|\uff08|\uff09|\u300a|\u300b|\u3008|\u3009|\u3010|\u3011|\u300e|\u300f|\u300c|\u300d|\ufe43|\ufe44|\u3014|\u3015|\u2026|\u2014|\uff5e|\ufe4f|\uffe5|\ ]+$", string, flags=re.I):
                    continue

                # 忽略单个字母和数字之类的 例如快捷键
                if re.match(r"^[a-z0-9]$", string, flags=re.I):
                    continue

                # 忽略特殊字符
                if re.match(r"^[0-9|\+\-\%]+$", string, flags=re.I):
                    continue
                # print("string:", string)
                yield string

    def restruct_strings(self):
        """
            提取字符串中需要汉化的字符串，剔除无关的字符
        """
        self.sentence_set = set([])
        temp_list = list(set(self.text_cache))
        for i, sentence in enumerate(temp_list):
            strings = list(self.take_string_from_sentense(sentence))
            self.sentence_set.update(strings)

    def check_result(self, eee, files):
        for file_name in files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)

            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                continue

            with open("%s.mta2.cache" % file_path, "r") as rf:
                contents = rf.readlines()
            for lineno, line in enumerate(contents):
                for e in eee:
                    if e in line:
                        print("[Break]:", file_name, lineno, e, line)
                        break

        print("[Done check]")


class TranslateWorkerForIni(BaseWorker):
    """
        target_dir: target map dir
    """
    def __init__(self, arg):
        super(TranslateWorkerForIni, self).__init__()
        self.arg = arg
        self.debug = False
        while self.arg["target_dir"][-1] == "/": self.arg["target_dir"] = self.arg["target_dir"][:-1]
        self.text_cache = []

    def grep_ini(self):
        """
            使用 ini parser
            将字符（英文/俄文）统一转化成小写
        """
        for file_name in ini_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            worker = ini_work_files[file_name]
            if not worker:
                continue

            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                continue

            wk = worker({"file_path": file_path})
            string_list = wk.grep_string_from_config()
            string_list = [x.lower() for x in string_list]
            # q.d()
            # exit()
            self.text_cache += string_list

        # print("self.text_cache:", self.text_cache)

    def write_translate_string(self, wf, line, string):
        """
            一行里只有一部分字符串是需要翻译的，例如
            line => aaa = "who am i?"
            string => "who am i?"
            trans_line => 我是谁
            结构 ==> aaa = "我是谁?"
        """

        # 去除字符串前后的标点空格和特殊字符
        # string = re.sub(r"^[\~\!\@\#\$\%\^\&\*\(\)\_\+\=\-\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?\s]*|[\~\!\@\#\$\%\^\&\*\(\)\_\+\=\-\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?\s]*$", "", string, flags=re.I)
        trans_line = string
        trans_strings = list(set([x.lower() for x in self.take_string_from_sentense(string)]))
        if trans_strings:
            # print("trans_strings:", set(trans_strings))
            good_key = self.trans_result_keys & set(trans_strings)
            good_key = list(good_key)
            if good_key:
                # print("good_key:", good_key)
                if not len(good_key) == len(set(trans_strings)):
                    print("len is not good")
                    q.d()
                    raise("1")
                good_trans = {x: self.trans_result[x] for x in good_key}
                # print("good_trans:", good_trans)
                good_key.sort(key=lambda x: -len(x))
                # print("trans_line:", trans_line.strip())
                for key in good_key:
                    trans_line = re.sub(re.escape(key), good_trans[key], trans_line, flags=re.I)
                    # trans_line = trans_line.replace(key, good_trans[key])
                # if "рыцарь" in good_key:
                #     q.d()
                # print("trans_line result:", trans_line)

        # if self.debug:
        #     q.d()
        # if "рыцарь" in line:
        #     print("".join(traceback.format_stack()))
        #     q.d()
        # print("line:", line)
        # print("string:", string)
        # print("trans_line:", trans_line)
        # q.d()
        # print("[Translate]:", line.strip())
        wf.write(line.replace(string, trans_line))

    def my_writer(self, file_path, work_item):

        with open(file_path, "r") as rf:
            contents = rf.readlines()
        with open("%s.mta2.cache" % file_path, "w") as wf:
            wait_end = False
            key_name = None
            wait_string = False
            wait_string2 = False
            for lineno, rawline in enumerate(contents):
                line = rawline
                try:

                    # 如果遇到跨行字符串
                    if wait_string:
                        append_string = line
                        # zz = ""

                        if line.strip() == "]=]" or line.strip() == "]=],":
                            wait_string = False
                            self.write_raw_string(wf, rawline)
                            continue

                        if line.strip()[-3:] == "]=]":
                            wait_string = False
                            append_string = line.strip()[:-3].strip()
                            # zz = line[line.find(append_string) + len(append_string):]
                        elif line.strip()[-4:] == "]=],":
                            wait_string = False
                            append_string = line.strip()[:-4].strip()
                            # zz = line[line.find(append_string) + len(append_string):]

                        if append_string:
                            if key_name.lower() in work_item:
                                self.write_translate_string(wf, rawline, append_string)
                                # if zz:
                                #     self.write_raw_string(wf, zz)
                            else:
                                self.write_raw_string(wf, rawline)
                            # ini_obj[sect_name][key_name].append(append_string)
                            # self.write_translate_string(wf, rawline, append_string)

                        continue

                    # 如果在跨行字符串 -> 对象
                    if wait_end:

                        # 如果遇到跨行字符串
                        if wait_string2:
                            append_string2 = line
                            # zz = ""

                            if line.strip() == "]=]" or line.strip() == "]=],":
                                wait_string2 = False
                                self.write_raw_string(wf, rawline)
                                continue

                            if line.strip()[-3:] == "]=]":
                                wait_string2 = False
                                append_string2 = line.strip()[:-3].strip()
                                # zz = line[line.find(append_string2) + len(append_string2):]
                            elif line.strip()[-4:] == "]=],":
                                wait_string2 = False
                                append_string2 = line.strip()[:-4].strip()
                                # zz = line[line.find(append_string2) + len(append_string2):]

                            if append_string2:

                                if key_name.lower() in work_item:
                                    self.write_translate_string(wf, rawline, append_string2)
                                    # if zz:
                                    #     self.write_raw_string(wf, zz)
                                else:
                                    self.write_raw_string(wf, rawline)
                                # ini_obj[sect_name][key_name].append(append_string2)
                                # ini_obj[sect_name][key_name][w_index].append(append_string2)
                                # self.write_translate_string(wf, rawline, append_string2)

                            continue

                        # 判断对象是否完结
                        if line.strip()[-1:] == "}":
                            wait_end = False
                            key_name = None
                            self.write_raw_string(wf, rawline)
                        elif line[-3:] == "[=[":
                            wait_string2 = True
                            # w_index = len(ini_obj[sect_name][key_name])
                            # ini_obj[sect_name][key_name].append([])
                            self.write_raw_string(wf, rawline)
                        else:
                            if key_name.lower() in work_item:
                                self.write_translate_string(wf, rawline, line)
                            else:
                                self.write_raw_string(wf, rawline)
                            # ini_obj[sect_name][key_name].append(line)
                            # self.write_translate_string(wf, rawline, line)

                        continue

                    else:
                        line = line.strip()
                        # 无视注释和空行
                        if not line or line[:2] == "--":
                            self.write_raw_string(wf, rawline)
                            continue

                    # 判断值是否对象
                    if line[-1:] == "{":
                        wait_end = True
                        key_name = line.split("=")[0].strip()
                        # ini_obj[sect_name][key_name] = []
                        self.write_raw_string(wf, rawline)
                    elif line[-3:] == "[=[":
                        wait_string = True
                        key_name = line.split("=")[0].strip()
                        # ini_obj[sect_name][key_name] = []
                        self.write_raw_string(wf, rawline)

                    # 判断是否新节点
                    # 未兼容 单行 [=[ 和 ]=] 同时存在的情况
                    elif re.match(r"^\[([a-z0-9]+)\]$", line, flags=re.I):
                        # sect_name = re.match(r"^\[([a-z0-9]+)\]$", line, re.I).group(1)
                        # ini_obj[sect_name] = {}
                        # print("Add new section: [%s]" % sect_name)
                        self.write_raw_string(wf, rawline)

                    elif re.match(r"^\[([^\[\]\"\']+)\]$", line, re.I):
                        # print("warn:", "Be not english:", line)
                        # sect_name = re.match(r"^\[([^\[\]\"\']+)\]$", line, re.I).group(1)
                        # ini_obj[sect_name] = {}
                        self.write_raw_string(wf, rawline)

                    # 直接赋值
                    elif "=" in line:
                        key_name = line.split("=")[0]
                        key_val = line[len(key_name) + 1:]
                        key_name = key_name.strip()

                        # if "рыцарь" in rawline:
                        #     print("".join(traceback.format_stack()))
                        #     q.d()
                        # ??????
                        if key_name.lower() in work_item:
                            self.write_translate_string(wf, rawline, key_val)
                        else:
                            self.write_raw_string(wf, rawline)
                    else:
                        print("[SKIP]", line)
                        self.write_raw_string(wf, rawline)
                        # raise Exception("[CANNOT PARSE]")

                except Exception:
                    print(traceback.format_exc())
                    q.d()

    def rewrite_ini(self):
        self.trans_result_keys = self.trans_result.keys()
        for file_name in ini_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            worker = ini_work_files[file_name]
            if not worker:
                continue

            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                continue

            work_item = worker.WORK_ITEM
            self.my_writer(file_path, work_item)


class TranslateWorkerForWts(BaseWorker):
    """docstring for TranslateWorkerForWts"""
    def __init__(self, arg):
        super(TranslateWorkerForWts, self).__init__()
        self.arg = arg
        while self.arg["target_dir"][-1] == "/": self.arg["target_dir"] = self.arg["target_dir"][:-1]
        self.text_cache = []

    def grep_wts(self):
        for file_name in wts_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            worker = wts_work_files[file_name]
            if not worker:
                continue

            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                continue

            wk = worker({"file_path": file_path})
            string_list = wk.grep_string_from_config()
            string_list = [x.strip().lower() for x in string_list]
            # q.d()
            # exit()
            self.text_cache += string_list

        # print("self.text_cache:", self.text_cache)

    def rewrite_wts(self):
        self.trans_result_keys = self.trans_result.keys()
        # self.trans_result_keys.sort(key=lambda x: -len(x))
        for file_name in wts_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                continue
            with open(file_path, "r") as rf:
                contents = rf.readlines()
                # contents = contents.replace("\r", "\1").replace("\n", "\2")

            with open("%s.mta2.cache" % file_path, "w") as wf:
                for lineno, rawline in enumerate(contents):
                    line = rawline

                    if re.match(r"^([\{\}]|(STRING [\d]+))$", line):
                        self.write_raw_string(wf, rawline)
                    else:
                        self.write_translate_string(wf, rawline, line)

                    # for key in self.trans_result_keys:
                    #     # q.d()
                    #     line = re.sub(re.escape(key), self.trans_result[key], line, flags=re.I)

                    # wf.write(line)

    def write_translate_string(self, wf, line, string):
        # 去除字符串前后的标点空格和特殊字符
        trans_line = string
        trans_strings = list(set([x.lower() for x in self.take_string_from_sentense(string)]))
        if trans_strings:
            # print("trans_strings:", set(trans_strings))
            good_key = self.trans_result_keys & set(trans_strings)
            good_key = list(good_key)
            if good_key:
                # print("good_key:", good_key)
                if not len(good_key) == len(set(trans_strings)):
                    print("len is not good")
                    q.d()
                good_trans = {x: self.trans_result[x] for x in good_key}
                # print("good_trans:", good_trans)
                good_key.sort(key=lambda x: -len(x))
                # print("trans_line:", trans_line.strip())
                for key in good_key:
                    trans_line = re.sub(re.escape(key), good_trans[key], trans_line, flags=re.I)

        wf.write(line.replace(string, trans_line))


class TranslateWorkerForJ(BaseWorker):
    """docstring for TranslateWorkerForJ"""
    def __init__(self, arg):
        super(TranslateWorkerForJ, self).__init__()
        self.arg = arg
        while self.arg["target_dir"][-1] == "/": self.arg["target_dir"] = self.arg["target_dir"][:-1]
        self.text_cache = []

    def fuck_reg2(self, string, sc="\""):
        ss = ""
        wait = False
        for i, c in enumerate(string):
            if wait:
                if c == sc and ss:
                    yield "%s%s%s" % (sc, ss, sc)
                    wait = False
                    ss = ""
                else:
                    ss += c
            elif c == sc:
                wait = True

    def grep_j(self):

        for file_name in jass_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            worker = jass_work_files[file_name]
            if not worker:
                continue

            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                continue

            wk = worker({"file_path": file_path})
            string_list = wk.grep_string_from_config()
            string_list = [x.strip().lower() for x in string_list]
            self.text_cache += string_list

    def rewrite_j(self):
        self.trans_result_keys = self.trans_result.keys()
        for file_name in jass_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                print("[EMPTY]:", file_path)
                continue
            with open(file_path, "r") as rf:
                contents = rf.readlines()

            with open("%s.mta2.cache" % file_path, "w") as wf:
                key_index = None
                wait_line1 = False
                for lineno, rawline in enumerate(contents):
                    line = rawline

                    if wait_line1:
                        # 双引号未闭合: 计算 " 但不计算 \"
                        if (line.count("\"") - line.count("\\\"")) % 2 == 0:
                            self.write_translate_string(wf, rawline, line, key_index, "middle")
                        else:
                            wait_line1 = False
                            self.write_translate_string(wf, rawline, line, key_index, "end")
                    elif re.match(War3mapJWorker.re_call, line, flags=re.I):
                        key_index = re.match(War3mapJWorker.re_call, line, flags=re.I).group(1)
                        if (line.count("\"") - line.count("\\\"")) % 2 == 1:
                            wait_line1 = True
                            self.write_translate_string(wf, rawline, line, key_index, "start")
                        else:
                            self.write_translate_string(wf, rawline, line, key_index, "inside")
                    else:
                        self.write_raw_string(wf, rawline)

                    # q.d()

    def do_re_sub(self, m):

        # print("m:", m)
        return m.group(1).replace(",", "\4")

    def fuck_reg(self, string):
        string2 = list(string)
        start_t = False
        for i, c in enumerate(string2):
            if start_t:
                if c == ",":
                    string2[i] = "\4"
                elif c == "\"":
                    start_t = False
            elif c == "\"":
                start_t = True

        return "".join(string2)

    def write_translate_string(self, wf, line, rawstring, key_index, mark):
        # 去除字符串前后的标点空格和特殊字符

        # 兼容平台换行格式
        while rawstring[-1:] == "\n":
            rawstring = rawstring[:-1]

        strings = []

        # 忽略空字符串 和 TRIGSTR_xx 等固定字符串
        if not rawstring or re.match(r"^TRIGSTR_[\d]+$", rawstring):
            return self.write_raw_string(wf, line)

        elif mark == "middle":
            strings.append(line)

        elif mark == "start":
            line = line.replace("\\\"", "\3")
            i_temp = line.rindex("\"")
            # r_string = line[i_temp:] + "\""
            r_string = line[i_temp:]
            strings.append(r_string)
            eline = line[:i_temp] + ")"

            rline = eline.replace("\\\"", "\3")
            rline = rline[rline.find("(") + 1: rline.rfind(")")]

            # 这里的正则表达式没写对，只匹配了第一个 "" 里面的字符串，如果有多个则不行
            # rline = re.sub(r"(\".*?\"){1,}", self.do_re_sub, rline, flags=re.I)
            rline = self.fuck_reg(rline)

            rline_list = rline.split(",")
            for i in War3mapJWorker.LINE_PLACE[key_index][:-1]:
                if len(rline_list) > i and rline_list[i]:
                    # strings.append(rline_list[i])
                    strings += self.fuck_reg2(rline_list[i])

        elif mark == "end":

            line = line.replace("\\\"", "\3")
            i_temp = line.index("\"")
            # l_string = "\"" + line[:i_temp + 1]
            l_string = line[:i_temp + 1]
            strings.append(l_string)
            eline = "(\"" + line[i_temp:]

            rline = eline.replace("\\\"", "\3")
            rline = rline[rline.find("(") + 1: rline.rfind(")")]

            # 这里的正则表达式没写对，只匹配了第一个 "" 里面的字符串，如果有多个则不行
            # rline = re.sub(r"(\".*?\")", self.do_re_sub, rline, flags=re.I)
            rline = self.fuck_reg(rline)

            rline_list = rline.split(",")
            ll = War3mapJWorker.LINE_PLACE[key_index][-1]
            for i in War3mapJWorker.LINE_PLACE[key_index][:-1]:
                if -len(rline_list) < i - ll and rline_list[i - ll]:
                    # strings.append(rline_list[i - ll])
                    strings += self.fuck_reg2(rline_list[i - ll])

        elif mark == "inside":

            # 去假双引号 (在字符串里)
            rline = rawstring.replace("\\\"", "\3")

            # 去括号
            rline = rline[rline.find("(") + 1: rline.rfind(")")]

            # 去假逗号 (在字符串里)
            # rline = re.sub(r"(\".*?\")", self.do_re_sub, rline, flags=re.I)
            rline = self.fuck_reg(rline)

            # 取目标字符串 (第x个参数)(不会这么惨，遇到嵌套方法的吧。。。)
            rline_list = rline.split(",")
            for i in War3mapJWorker.LINE_PLACE[key_index][:-1]:
                if len(rline_list) > i and rline_list[i]:
                    # temp_string = rline_list[i]
                    # strings.append(temp_string)
                    strings += self.fuck_reg2(rline_list[i])

        # 后面会split的
        # string = ".,".join(strings)
        for string in strings:

            # 还原string
            string = string.strip().replace("\4", ",")

            # 判断 string 长度，剔除非 "字符串" 和 空字符串
            if len(string) >= 3 and ((
                mark == "start" and string[0] == "\"") or (
                mark == "end" and string[-1] == "\"") or (
                mark == "middle") or (
                mark == "inside" and string[0] == string[-1] == "\""
            )):
                # 去首尾的 双引号
                # string = string[1:-1]
                pass

            else:
                print("SKip string in J:", string, mark)
                string = ""

            trans_line = string
            trans_strings = ""
            if string:
                trans_strings = list(set([x.lower() for x in self.take_string_from_sentense(string)]))

            if trans_strings:
                # print("trans_strings:", set(trans_strings))
                good_key = self.trans_result_keys & set(trans_strings)
                good_key = list(good_key)
                if good_key:
                    # print("good_key:", good_key)
                    if not len(good_key) == len(set(trans_strings)):
                        print("len is not good")
                        q.d()
                    good_trans = {x: self.trans_result[x] for x in good_key}
                    # print("good_trans:", good_trans)
                    good_key.sort(key=lambda x: -len(x))
                    # print("trans_line:", trans_line.strip())
                    for key in good_key:
                        trans_line = re.sub(re.escape(key), good_trans[key], trans_line, flags=re.I)

            line = re.sub(re.escape(string), trans_line, line, flags=re.I)

        wf.write(line)

