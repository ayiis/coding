"""
    1. 只有字符串会跨行，其他都是1行
    2. 字符串跨行都是 " 未闭合
    3. 每行通常只有一个操作
"""
import q
import re


class Worker(object):
    """
        docstring for Worker
    """
    WORK_ITEM = [
        "QuestMessageBJ", "CreateQuestBJ", "CreateTextTagLocBJ", "QuestSetDescriptionBJ",
        "DisplayTimedTextToForce", "DialogAddButtonBJ", "SetMapDescription", "DisplayTextToPlayer",
        "DisplayTextToForce", "DisplayTimedTextToPlayer",
        "CustomDefeatBJ", "DialogSetMessageBJ", "MultiboardSetItemValueBJ",
        "CreateTextTagUnitBJ", "SetPlayerName",
        "TransmissionFromUnitWithNameBJ", "CreateQuestItemBJ"
    ]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]

    # 字符串位置*N, 参数数量
    LINE_PLACE = {
        "QuestMessageBJ": [2, 3],
        "CreateQuestBJ": [1, 2, 4],
        "CreateTextTagLocBJ": [0, 8],
        "QuestSetDescriptionBJ": [1, 2],
        "DisplayTimedTextToForce": [2, 3],
        "DialogAddButtonBJ": [1, 2],
        "SetMapDescription": [0, 1],
        "SetMapName": [0, 1],
        "BJDebugMsg": [0, 1],
        "SetTextTagText": [1, 3],
        "DisplayTextToPlayer": [3, 4],
        "DisplayTextToForce": [1, 2],
        "DisplayTimedTextToPlayer": [4, 5],
        "CustomDefeatBJ": [1, 2],
        "DialogSetMessageBJ": [0, 2],
        "MultiboardSetItemValueBJ": [3, 4],
        "CreateTextTagUnitBJ": [0, 8],
        "SetPlayerName": [1, 2],
        "TransmissionFromUnitWithNameBJ": [2, 4, 8],
        "CreateQuestItemBJ": [1, 2],
    }
    re_call = r"^[\s]*call[\s]+(%s)" % "|".join(WORK_ITEM)

    def __init__(self, arg):
        super(Worker, self).__init__()
        self.arg = arg

    def do_re_sub(self, m):

        # print("m:", m.group(1))

        return m.group(1).replace(",", "\4")

    def f_index(self, string, c):
        for i, s in enumerate(string):
            if s == c:
                yield i

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

    def get_string_from(self, wts_obj, key_index, rawstring, mark):

        strings = []
        line = rawstring

        if not line:
            strings = [""]

        elif mark == "middle":
            strings.append("\"%s\"" % line)

        elif mark == "start":
            # if key_index in ("QuestMessageBJ", ""):
            #     pass
            # string = line.replace("\\\"", "\3").split("\"")[-1].replace("\3", "\\\"")
            line = line.replace("\\\"", "\3")
            i_temp = line.rindex("\"")
            r_string = line[i_temp:] + "\""
            strings.append(r_string)
            eline = line[:i_temp] + ")"

            rline = eline.replace("\\\"", "\3")
            rline = rline[rline.find("(") + 1: rline.rfind(")")]

            # 这里的正则表达式没写对，只匹配了第一个 "" 里面的字符串，如果有多个则不行
            # rline = re.sub(r"(\".*?\"){1,}", self.do_re_sub, rline, flags=re.I)
            rline = self.fuck_reg(rline)

            rline_list = rline.split(",")
            for i in self.LINE_PLACE[key_index][:-1]:
                if len(rline_list) > i and rline_list[i]:
                    # strings.append(rline_list[i])
                    strings += self.fuck_reg2(rline_list[i])

            # print("[start] rawstring:", rawstring)
            # print("strings:", len(strings), strings)

        elif mark == "end":
            # string = line.replace("\\\"", "\3").split("\"")[0].replace("\3", "\\\"")
            # return re.match(r"(.*([^\\]))(\").*", line).group(1)

            line = line.replace("\\\"", "\3")
            i_temp = line.index("\"")
            l_string = "\"" + line[:i_temp + 1]
            strings.append(l_string)
            eline = "(\"" + line[i_temp:]

            rline = eline.replace("\\\"", "\3")
            rline = rline[rline.find("(") + 1: rline.rfind(")")]

            # 这里的正则表达式没写对，只匹配了第一个 "" 里面的字符串，如果有多个则不行
            # rline = re.sub(r"(\".*?\")", self.do_re_sub, rline, flags=re.I)
            rline = self.fuck_reg(rline)

            rline_list = rline.split(",")
            ll = self.LINE_PLACE[key_index][-1]
            for i in self.LINE_PLACE[key_index][:-1]:
                if -len(rline_list) < i - ll and rline_list[i - ll]:
                    # strings.append(rline_list[i - ll])
                    strings += self.fuck_reg2(rline_list[i - ll])

            # print("[end] rawstring:", rawstring)
            # print("strings:", len(strings), strings)

        elif mark == "in":

            # 去假双引号 (在字符串里)
            rline = rawstring.replace("\\\"", "\3")

            # 去括号
            rline = rline[rline.find("(") + 1: rline.rfind(")")]

            # 去假逗号 (在字符串里)
            # rline = re.sub(r"(\".*?\")", self.do_re_sub, rline, flags=re.I)
            rline = self.fuck_reg(rline)

            # 取目标字符串 (第x个参数)
            rline_list = rline.split(",")
            for i in self.LINE_PLACE[key_index][:-1]:
                if len(rline_list) > i and rline_list[i]:
                    # strings.append(rline_list[i])
                    strings += self.fuck_reg2(rline_list[i])

        for i, string in enumerate(strings):
            # 判断 string 长度，剔除非 "字符串" 和 空字符串
            if len(string) >= 3 and string[0] == string[-1] == "\"":
                # strings[i] = string[1:-1]
                pass
            else:
                # q.d()
                strings[i] = ""

            if re.match(r"^TRIGSTR_[0-9]+$", string, flags=re.I):
                print("am i?", string)
                strings[i] = ""

        # for string in strings:
            # # 后面会split的
            # string = ",".join(strings)

            # 还原string
            string = string.strip().replace("\4", ",")

            # 判断 string 长度，剔除非 "字符串" 和 空字符串
            # if len(string) >= 3 and string[0] == string[-1] == "\"":

            #     # 去首尾的 双引号
            #     string = string[1:-1]
            #     # pass

            # else:
            #     string = ""

            # if "TRIGSTR_111" in rawstring:
            #     q.d()

            # if "герой древности" in rawstring.lower():
            #     q.d()

            # 忽略空字符串 和 TRIGSTR_xx 等固定字符串
            if not string or re.match(r"^TRIGSTR_[0-9]+$", string, flags=re.I):
                pass
            else:
                wts_obj[key_index].append(string)

            # q.d()

    def grep_string_from_config(self):
        string_list = []
        with open(self.arg["file_path"], "r") as rf:
            contents = rf.readlines()
        wts_obj = {}
        key_index = None
        wait_line1 = False
        for lineno, rawline in enumerate(contents):
            line = rawline

            # 兼容平台换行格式
            while line[-1:] == "\n":
                line = line[:-1]

            if wait_line1:
                # 双引号未闭合: 计算 " 但不计算 \"
                if (line.count("\"") - line.count("\\\"")) % 2 == 0:
                    self.get_string_from(wts_obj, key_index, line, "middle")
                else:
                    wait_line1 = False
                    self.get_string_from(wts_obj, key_index, line, "end")
            elif re.match(self.re_call, line, flags=re.I):
                key_index = re.match(self.re_call, line, flags=re.I).group(1)
                if key_index not in wts_obj:
                    wts_obj[key_index] = []

                if (line.count("\"") - line.count("\\\"")) % 2 == 1:
                    wait_line1 = True
                    self.get_string_from(wts_obj, key_index, line, "start")
                else:
                    self.get_string_from(wts_obj, key_index, line, "in")
            else:
                pass

        for i in wts_obj:
            string_list += wts_obj[i]

        return string_list


def test():
    wk = Worker({
        "file_path": "/mine/war3work/(2)Game of Life and Death-v2/map/war3map.2.j"
    })
    string_list = wk.grep_string_from_config()
    print("string_list:", string_list)


if __name__ == "__main__":
    test()
