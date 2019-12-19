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
from lib.w_common_ini import (
    AbilityWorker,
    BuffWorker,
    DestructableWorker,
    DoodadWorker,
    ItemWorker,
    UnitWorker,
    UpgradeWorker,
)

lni_work_files = {
    # "table/ability2.ini": AbilityWorker,

    # "map/war3mapskin.txt": War3mapskinWorker,

    # "table/ability.ini": AbilityWorker,
    # "table/buff.ini": BuffWorker,
    # "table/destructable.ini": DestructableWorker,
    # "table/doodad.ini": DoodadWorker,
    # "table/item.ini": ItemWorker,
    # "table/unit.ini": UnitWorker,
    # "table/upgrade.ini": UpgradeWorker,

    # "table/w3i.ini": None,
}

slk_work_fils = {

}

wts_work_files = {
    "map/war3map.wts": War3mapWtsWorker,
}

jass_work_files = {
    "map/war3map.j": None,
}


def get_files():
    pass


def build(source_path="templates_jade", target_path="templates", recursive=True):

    if not Path(target_path).exists():
        os.makedirs(target_path)
    elif not Path(target_path).is_dir():
        raise Exception("%s is not a dir!" % target_path)

    for path in Path(source_path).glob("*"):
        path_string = "%s" % path

        if recursive and path.is_dir():
            build("%s/%s" % (source_path, path.name), "%s/%s" % (target_path, path.name))

        elif path.is_file() and path_string[-5:] == ".jade" and len(path_string) > 5:
            pass


class TranslateWorkerForIni(object):
    """
        target_dir: target map dir
    """
    def __init__(self, arg):
        super(TranslateWorkerForIni, self).__init__()
        self.arg = arg
        while self.arg["target_dir"][-1] == "/": self.arg["target_dir"] = self.arg["target_dir"][:-1]
        self.text_cache = []

    def grep_ini(self):
        """
            使用 ini parser
            将字符（英文/俄文）统一转化成小写
        """
        for file_name in lni_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            worker = lni_work_files[file_name]
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

    def restruct_strings(self):
        """
            提取字符串中需要汉化的字符串，剔除无关的字符
        """
        self.sentence_set = set([])
        temp_list = list(set(self.text_cache))
        for i, sentence in enumerate(temp_list):
            strings = list(self.take_string_from_sentense(sentence))
            self.sentence_set.update(strings)

        # tt = list(self.sentence_set)
        # tt.sort(key=lambda x: len(x))
        # print("self.sentence_set:", tt)
        # exit()

    def take_string_from_sentense(self, sentence):
        # 包含 + - % 0-9 因为只是数字不同的技能实在太多了
        temp = re.sub(r"(\<[a-z0-9]{4},[a-z0-9]+\>|\|c[0-9a-f]{8}|[0-9\+\-\%]|\|n|\|r|[\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?])", "*", sentence, flags=re.I)
        # # 除外 + - % 0-9
        # temp = re.sub(r"(\|c[0-9a-f]{8}|\|n|\|r|[\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?])", "*", sentence, flags=re.I)
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

                yield string

    def do_translate(self, translater):

        try:
            self.trans_result = {}
            fy = translation_tool.init_fanyi(translater, "ru", "zh")
            for sentence in self.sentence_set:

                # 多加try保平安
                try:
                    res = fy.translate(sentence)
                    self.trans_result[sentence] = res
                except Exception:
                    print(traceback.format_exc())

            # print("self.trans_result:", self.trans_result)
        except Exception:
            print(traceback.format_exc())
            pass

        finally:
            fy.save_result()

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
        trans_strings = [x.lower() for x in self.take_string_from_sentense(string)]
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
                    # trans_line = trans_line.replace(key, good_trans[key])
                # if "рыцарь" in good_key:
                #     q.d()
                # print("trans_line result:", trans_line)

        # if "рыцарь" in line:
        #     print("".join(traceback.format_stack()))
        #     q.d()
        # print("line:", line)
        # print("string:", string)
        # print("trans_line:", trans_line)
        # q.d()
        wf.write(line.replace(string, trans_line))

    def write_raw_string(self, wf, line):
        # if "рыцарь" in line:
        #     print("".join(traceback.format_stack()))
        #     q.d()
        wf.write(line)

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

                        if line.strip()[-3:] == "]=]":
                            wait_string = False
                            append_string = line.strip()[:-3].strip()
                        elif line.strip()[-4:] == "]=],":
                            wait_string = False
                            append_string = line.strip()[:-4].strip()

                        if append_string:
                            # ini_obj[sect_name][key_name].append(append_string)
                            self.write_translate_string(wf, rawline, append_string)

                        continue

                    # 如果在跨行字符串 -> 对象
                    if wait_end:

                        # 如果遇到跨行字符串
                        if wait_string2:
                            append_string2 = line

                            if line.strip()[-3:] == "]=]":
                                wait_string2 = False
                                append_string2 = line.strip()[:-3].strip()
                            elif line.strip()[-4:] == "]=],":
                                wait_string2 = False
                                append_string2 = line.strip()[:-4].strip()

                            if append_string2:
                                # ini_obj[sect_name][key_name].append(append_string2)
                                # ini_obj[sect_name][key_name][w_index].append(append_string2)
                                self.write_translate_string(wf, rawline, append_string2)

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
                            # ini_obj[sect_name][key_name].append(line)
                            self.write_translate_string(wf, rawline, line)

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
                        # key_name = line.split("=")[0].strip()
                        # ini_obj[sect_name][key_name] = []
                        self.write_raw_string(wf, rawline)
                    elif line[-3:] == "[=[":
                        wait_string = True
                        # key_name = line.split("=")[0].strip()
                        # ini_obj[sect_name][key_name] = []
                        self.write_raw_string(wf, rawline)

                    # 判断是否新节点
                    # 未兼容 单行 [=[ 和 ]=] 同时存在的情况
                    elif re.match(r"^\[([a-z0-9]+)\]$", line, flags=re.I):
                        # sect_name = re.match(r"^\[([a-z0-9]+)\]$", line, re.I).group(1)
                        # ini_obj[sect_name] = {}
                        # print("Add new section: [%s]" % sect_name)
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
                        raise Exception("[CANNOT PARSE]")

                except Exception:
                    print(traceback.format_exc())
                    q.d()

    def rewrite_ini(self):
        self.trans_result_keys = self.trans_result.keys()
        for file_name in lni_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
            worker = lni_work_files[file_name]
            if not worker:
                continue

            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                continue

            work_item = worker.WORK_ITEM
            self.my_writer(file_path, work_item)


class TranslateWorkerForWts(object):
    """docstring for TranslateWorkerForWts"""
    def __init__(self, arg):
        super(TranslateWorkerForWts, self).__init__()
        self.arg = arg
        while self.arg["target_dir"][-1] == "/": self.arg["target_dir"] = self.arg["target_dir"][:-1]
        self.text_cache = []

    def take_string_from_sentense(self, sentence):
        # 包含 + - % 0-9 因为只是数字不同的技能实在太多了
        temp = re.sub(r"(\<[a-z0-9]{4},[a-z0-9]+\>|\|c[0-9a-f]{8}|[0-9\+\-\%]|\|n|\|r|[\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?])", "*", sentence, flags=re.I)
        # # 除外 + - % 0-9
        # temp = re.sub(r"(\|c[0-9a-f]{8}|\|n|\|r|[\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?])", "*", sentence, flags=re.I)
        for string in temp.split("*"):
            string = string.strip()
            if string:

                # if "Игроки получают 150% опыта".lower() in sentence:
                #     q.d()

                # 中文和标点符号就放过了吧，老铁
                if re.match(r"^[\u4e00-\u9fa5\u3002|\uff1f|\uff01|\uff0c|\u3001|\uff1b|\uff1a|\u201c|\u201d|\u2018|\u2019|\uff08|\uff09|\u300a|\u300b|\u3008|\u3009|\u3010|\u3011|\u300e|\u300f|\u300c|\u300d|\ufe43|\ufe44|\u3014|\u3015|\u2026|\u2014|\uff5e|\ufe4f|\uffe5|\ ]+$", string, flags=re.I):
                    continue

                # 忽略单个字母和数字之类的 例如快捷键
                if re.match(r"^[a-z0-9]$", string, flags=re.I):
                    continue

                # 忽略特殊字符
                if re.match(r"^[0-9|\+\-\%]+$", string, flags=re.I):
                    continue

                yield string

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

    def restruct_strings(self):
        """
            直接整个字符串丢进去翻译，不处理
            NO - TODO THIS
        """
        self.sentence_set = set([])
        temp_list = list(set(self.text_cache))
        for i, sentence in enumerate(temp_list):
            strings = list(self.take_string_from_sentense(sentence))
            self.sentence_set.update(strings)

        # tt = list(self.sentence_set)
        # tt.sort(key=lambda x: len(x))

    def do_translate(self, translater):

        try:
            self.trans_result = {}
            fy = translation_tool.init_fanyi(translater, "ru", "zh")
            for sentence in self.sentence_set:

                # 多加try保平安
                try:
                    res = fy.translate(sentence)
                    self.trans_result[sentence] = res
                except Exception:
                    print(traceback.format_exc())

                # break

            # print("self.trans_result:", self.trans_result)
        except Exception:
            print(traceback.format_exc())
            pass

        finally:
            fy.save_result()

    def rewrite_wts(self):
        self.trans_result_keys = self.trans_result.keys()
        # self.trans_result_keys.sort(key=lambda x: -len(x))
        for file_name in wts_work_files:
            file_path = "%s/%s" % (self.arg["target_dir"], file_name)
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

    def write_raw_string(self, wf, line):
        # if "рыцарь" in line:
        #     print("".join(traceback.format_stack()))
        #     q.d()
        wf.write(line)

    def write_translate_string(self, wf, line, string):
        # 去除字符串前后的标点空格和特殊字符
        trans_line = string
        trans_strings = [x.lower() for x in self.take_string_from_sentense(string)]
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


def test():

    if not Path("./data/").is_dir():
        os.mkdir("./data/")

    if False:
        fy = translation_tool.init_fanyi("test", "ru", "zh")
        res = fy.translate("test")
        print("res:", res)

    if False:
        arg = {
            "target_dir": "/mine/war3work/(2)Game of Life and Death-v2/",
        }
        tw = TranslateWorkerForIni(arg)
        tw.grep_ini()
        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        # print("sentence_set:", tw.sentence_set)
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test")
        # tw.do_translate("baidu")
        # print("trans_result:", tw.trans_result)
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_ini()

    if True:
        arg = {
            "target_dir": "/mine/war3work/(2)Game of Life and Death-v2/",
        }
        tw = TranslateWorkerForWts(arg)
        tw.grep_wts()

        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()

        # tw.do_translate("test")
        tw.do_translate("baidu")
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_wts()


if __name__ == "__main__":
    test()
