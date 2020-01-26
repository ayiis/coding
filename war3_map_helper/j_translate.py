"""
    熟悉 LISP 有助于语法分析
"""
import q
import re
import traceback

WORK_ITEM = [
    "QuestMessageBJ", "CreateQuestBJ", "CreateTextTagLocBJ", "QuestSetDescriptionBJ",
    "DisplayTimedTextToForce", "DialogAddButtonBJ", "SetMapDescription", "DisplayTextToPlayer",
    "DisplayTextToForce", "DisplayTimedTextToPlayer",
    "CustomDefeatBJ", "DialogSetMessageBJ", "MultiboardSetItemValueBJ",
    "CreateTextTagUnitBJ", "SetPlayerName", "SetMapName",
    "TransmissionFromUnitWithNameBJ", "CreateQuestItemBJ",
    "TransmissionFromUnitTypeWithNameBJ", "CreateMultiboardBJ",
    "QuestSetTitleBJ", "CreateTimerDialogBJ",
    # "Preload",  # ?
]
# WORK_ITEM = set([x.lower() for x in WORK_ITEM])
WORK_ITEM = set(WORK_ITEM)

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
    "TransmissionFromUnitTypeWithNameBJ": [3, 6, 10],
    "CreateMultiboardBJ": [2, 3],
    "QuestSetTitleBJ": [1, 2],
    "CreateTimerDialogBJ": [1, 2],
    # "Preload": [0, 1],    # ?
}

CATCH_PLE = {
    "[": ["[", "]"],
    "(": ["(", ")"],
}

DEBUG = False


def translate(word):
    print("[translate]", word.replace("\n", "\\n"))
    # return "\"*AY_STRING_HERE\""

    return word


COMMON_TRANSLATE_WRAP = {
    "translate": translate,
}


class SentenseStruct(object):
    def __init__(self):
        super(SentenseStruct, self).__init__()
        self.name = ""
        self._parent = None
        self._index = 0     # 目前是第几个参数
        self._para_count = 0    # 目前参数数量
        self._para_total_count = 0    # 参数总数数量
        self._para_list = []    # 参数列表

    def set_name(self, name):
        self.name = name

    def get_parent(self):
        return self._parent

    def add_para(self, para):
        self._para_list.append(para)

    def get_para_list(self):
        return self._para_list


class EmptyWorker(object):
    def __init__(self):
        pass

    def add_next_word(self, word):
        pass

    def end_sentense(self):
        pass

    def get_translate_result(self):
        pass

    def start_add_para(self):
        pass


class CallWorker(object):

    def __init__(self):
        self.buff = ""
        self.worker = self
        self.name = None
        self.function_deep = 0
        self.para_list = []
        self.parent = None
        self.para_index = 0
        self.tmp_para = None
        self.is_top = False

    def set_name(self, name):
        self.worker.name = name

    def set_self(self, worker):
        self.worker = worker

    def start_add_para(self):
        self.worker.tmp_para = []

    def add_para(self, para):
        self.worker.tmp_para.append(para)

    def update_last_para(self, para):
        self.worker.tmp_para[-1] = para

    def end_add_para(self):
        if self.worker.tmp_para is None:
            pass
        else:
            self.worker.para_list.append(self.worker.tmp_para)
            self.worker.para_index += 1
            self.worker.tmp_para = []

    def add_next_word(self, word):

        # print("add_next_word: ", word)

        # 空格不会跟其他word在一起，只要判断1次是否空格就行了，空格就跳过
        if not word.strip():
            return
        else:
            pass

        # print("word:", word)
        # # 第一个是函数名
        # if not self.worker.name:
        #     # print("In here for 1's")
        #     self.worker.set_name(word)
        #     self.worker.is_top = True

        if False:
            pass

        elif word in ("(", "["):
            # self.worker.end_add_para()

            # 创建一个新的子worker，设置自己为父worker，
            # print("new worker:", not self.worker.is_top)
            if not self.worker.is_top:
                new_worker = CallWorker()
                # new_worker.set_name(self.worker.tmp_para[-1])
                try:
                    if not self.worker.tmp_para:
                        # q.d()
                        # self.worker.tmp_para.append("")
                        self.worker.add_para("")

                    new_worker.name = self.worker.tmp_para[-1]
                except Exception as e:
                    print(e)
                    exit(1)
                # self.set_self(new_worker)
                new_worker.parent = self.worker
                self.worker = new_worker
            else:
                self.worker.is_top = False
            self.worker.start_add_para()
            self.worker.add_para(word)
            self.worker.end_add_para()
            self.worker.start_add_para()

        elif word in (")", "]"):

            self.worker.end_add_para()
            # print("-->", self.worker.name, ":")
            # print(self.worker.para_list)
            # {self.worker.name: self.worker.para_list}
            # print_all(self.worker)
            # self.worker.set_self(parent_ss)
            # q.d()
            # q.d()
            parent_ss = self.worker.parent
            if parent_ss.name is not None:
                parent_ss.update_last_para({self.worker.name: self.worker.para_list})
                self.worker = parent_ss
            else:
                # print("!!!!!!")
                # q.d()
                # self.worker = None
                self.para_list = {self.worker.name: self.worker.para_list}
            # q.d()
            # self.worker.para_list[-1] = {self.worker.name: self.worker.para_list}

        elif word == ",":
            self.worker.end_add_para()
            self.worker.start_add_para()

        else:

            # DO STRING
            # if self.worker.name in WORK_ITEM:
            #     if len(self.para_list) in LINE_PLACE[self.worker.name][:-1]:
            #         # print("This is string:", word.replace("\n", "\\n"))
            #         word = "*AY_STRING_HERE"

            self.worker.add_para(word)

    def end_sentense(self):
        pass

    def get_translate_result(self):

        def loop_obj_0(obj, p, name, i):

            # This is the para of string
            if name in WORK_ITEM and i in LINE_PLACE[name][:-1]:

                return p.join([((item and item[0] == "\"") and COMMON_TRANSLATE_WRAP["translate"](item) or item) for item in obj])

                # for item in obj:
                #     if item[0] == "\"":
                #         return translate(obj)
                #     else:
                #         return obj

            if type(obj) is str:
                return obj

            if type(obj) is list:
                return p.join([loop_obj(x, " ", name, k) for k, x in enumerate(obj)])

            elif type(obj) is dict:
                for key in obj:
                    left_c, right_c = CATCH_PLE[obj[key][0][0]]
                    return "%s%s%s%s" % (key, left_c, loop_obj(obj[key][1:], ", ", key, i), right_c)

        def loop_obj(obj, p, name, i):

            # This is the para of string
            if type(obj) is list and name in WORK_ITEM and i in LINE_PLACE[name][:-1]:

                re2 = []
                # q.d()
                # if type(obj) is dict:
                for item in obj:
                    # q.d()
                    if type(item) is str and item[0] == "\"":
                        re2.append(COMMON_TRANSLATE_WRAP["translate"](item))
                    elif type(item) is list:
                        re2.append(loop_obj(item, " ", name, i))
                    elif type(item) is dict:
                        re2.append(loop_obj(item, ", ", name, i))
                    else:
                        # print("wtf????")
                        # q.d()
                        re2.append(item)

                # elif type(obj) is list:
                #     return p.join([((item and item[0] == "\"") and translate(item) or item) for item in obj])
                # else:
                #     "wtf?"
                #     q.d()

                # q.d()
                return p.join(re2)

            if type(obj) is str:
                return obj

            if type(obj) is list:
                return p.join([loop_obj(x, " ", name, k) for k, x in enumerate(obj)])

            elif type(obj) is dict:
                for key in obj:
                    left_c, right_c = CATCH_PLE[obj[key][0][0]]
                    if key == "":
                        return "%s%s%s%s" % (key, left_c, loop_obj(obj[key][1:], ", ", name, i), right_c)
                    else:
                        return "%s%s%s%s" % (key, left_c, loop_obj(obj[key][1:], ", ", key, i), right_c)

        # print(self.para_list)
        # q.d()
        ree = loop_obj(self.para_list, ", ", "", 0)
        # print(ree)
        # print()
        # q.d()
        return ree


def print_all(wk, split_no=1):
    split_line = split_no * "  "
    if wk.name:
        print("%sname: %s" % (split_line, wk.name))
    if wk.parent and wk.parent != wk:
        print_all(wk.parent, split_no + 1)


class SentenseWorker(object):

    CAN_HANDLE_TYPE = ("CALL", "SET")
    OPERATORS = ("+", "-", "*", "/", "%", "or", "and", ">", ">=", "==", "!=", "<=", "<")    # , "*-", "/-")

    def __init__(self):
        self.type = None
        self._worker = None
        self.first_word = True

    def add_next_word(self, word):
        if self._worker:
            if self.first_word:
                self.first_word = False
                self._worker.start_add_para()

            self._worker.add_next_word(word)
        else:
            pass

    def add_first_word(self, first_word):

        if first_word == "call":
            self._worker = CallWorker()
            # self._worker.set_self(self._worker)
            # self.type = "CALL"

        elif first_word == "set":
            self._worker = EmptyWorker()
            # self.type = "SET"

        else:
            self._worker = EmptyWorker()

    def end_sentense(self):

        try:
            self._worker.end_sentense()
            pass
        except Exception as e:
            q.d()

    def get_translate_result(self):
        return self._worker.get_translate_result()


class Worker(object):
    """
        (-1+1) and (1-1) is hard to split, ignore for now
    """
    KEYWORD = r"^([\W]|\=\=|\!\=|\>\=|\<\=|\w+|\s+|//|(?=^([^\.]*\.?[^\.]*)$)[0-9a-f\.]+)$"
    PAD = " " * 4
    PAD_PLUS = ("function", "globals", "if", "loop")
    PAD_TWICE = ("elseif", "else")
    PAD_MINUS = ("endfunction", "endglobals", "endif", "endloop")

    def __init__(self, arg):
        super(Worker, self).__init__()
        self.arg = arg
        self.fp = open(arg["file_path"], "r")
        self.pre_char = ""
        self.line_pad = 0
        # self.line_no = 0
        self.pad_twice = False
        self.status = {
            "in_escape": False,
            "in_note": False,
            "in_string": False,
            "in_quote_string": False,
        }
        self.debug = False

    def read_next_word(self):
        """
            read \\w* and \\w{1}
            已知问题:
                self.pre_char 会影响下一次
        """
        buf, line_end = "", False
        while True:
            if self.pre_char:
                # has_pre = True
                char = self.pre_char
                self.pre_char = ""
            else:
                char = self.fp.read(1)

            if not char:
                raise Exception("EOF")

            if self.status["in_note"]:
                if char == "\n":
                    line_end = True
                    break
                else:
                    buf += char
                    continue
            else:
                pass

            if self.status["in_escape"]:
                self.status["in_escape"] = False
                buf += char
                continue
            else:
                pass

            if self.status["in_string"]:

                if char == "\\":
                    buf += char
                    self.status["in_escape"] = True
                    continue
                else:
                    pass

                if char == "\"":
                    self.status["in_string"] = False
                else:
                    pass

                buf += char
                continue
            else:
                pass

            if self.status["in_quote_string"]:
                if char == "\'":
                    self.status["in_quote_string"] = False
                else:
                    pass
                buf += char
                continue
            else:
                pass

            if char == "\n":
                line_end = True
                break
            else:
                pass

            if not buf:
                # something useless, but useful in split name and operator
                if char == " ":
                    buf += char
                    continue
                else:
                    pass

                if char == "\"":
                    buf += char
                    self.status["in_string"] = True
                    continue
                else:
                    pass

                if char == "\'":
                    buf += char
                    self.status["in_quote_string"] = True
                    continue
                else:
                    pass

                # handle the // note
                if char == "/":
                    if buf == "/":
                        buf += char
                        self.status["in_note"] = True
                        continue
                    else:
                        buf += char
                        break
                else:
                    pass
            else:
                pass

            tmp_buf = buf + char

            if not re.search(self.KEYWORD, tmp_buf, re.I):
                self.pre_char = char
                break
            else:
                buf = tmp_buf
                continue

        return buf, line_end

    def read_next_sentense(self):
        first_word = ""
        buf = ""
        # is_call = False
        # ss = None
        # function_deep = 0
        sw = SentenseWorker()
        while True:
            word, new_line = self.read_next_word()

            # pass `call`
            if not first_word:
                first_word = word
                sw.add_first_word(word)
            else:
                sw.add_next_word(word)
            # if word.strip():
            #     # handle the strings
            #     if word[0] == "\"":
            #         self.fp_debug.write("%s\r\n" % word.replace("\n", "\\n"))
            #         if len(word) > 300:
            #             print("string too long:", word)

            buf += word

            if new_line:
                buf += "\n"
                # self.line_no += 1
                # print(">", self.line_no, buf[:20])
                sw.end_sentense()
                break

        # if ss:
        #     print("get_para_list:", ss.get_para_list())

        # print(buf, first_word)
        if first_word == "call":
            # print("------" * 16)
            # print(buf)
            ree = "call " + sw.get_translate_result()
            ree += "\n"
            buf = ree

            # print(ree)
            # FOR DEBUG
            if DEBUG:
                if buf.replace(" ", "") != ree.replace(" ", ""):
                    print("x" * 16)
                    q.d()
                else:
                    pass
                # print("pass one!")
        # q.d()
        # exit(1)
        return buf, first_word

    def work(self):

        self.fp_write = open("%s.translate.j" % self.arg["file_path"], "w")
        self.fp_debug = open("%s.debug.2.j" % self.arg["file_path"], "w")
        while True:
            try:
                sentense, first_word = self.read_next_sentense()
            except Exception as e:
                if str(e) == "EOF":
                    print("EOF!")
                    break

                print(traceback.format_exc())
                q.d()

            self.fp_write.write(sentense)

        self.fp_write.close()
        self.fp_debug.close()

    def grep_string(self):

        self.result_list = []

        def _wrap(word):
            self.result_list += word.split("\n")
            # self.result_list.append(word)
            return word

        COMMON_TRANSLATE_WRAP["translate"] = _wrap

        while True:
            try:
                sentense, first_word = self.read_next_sentense()
            except Exception as e:
                if str(e) == "EOF":
                    print("EOF!")
                    break

                print(traceback.format_exc())
                q.d()

        return self.result_list

    def rewrite_j(self, _wrap, new_file_path):

        COMMON_TRANSLATE_WRAP["translate"] = _wrap
        self.fp_write = open(new_file_path, "w")

        while True:
            try:
                sentense, first_word = self.read_next_sentense()
            except Exception as e:
                if str(e) == "EOF":
                    print("EOF!")
                    break

                print(traceback.format_exc())
                q.d()

            self.fp_write.write(sentense)

        self.fp_write.close()


def main(file_path):
    # # function CreateAllDestructables takes nothing nothing, nothing nothing returns nothing
    # worker = Worker({"file_path": file_path})
    # worker.work()

    worker = Worker({"file_path": file_path})
    re = worker.grep_string()
    print("worker:", re)


if __name__ == "__main__":

    # file_path = "/mine/github/coding/temp/data/2.j"
    # file_path = "/mine/github/coding/temp/data/1.j"
    file_path = "/mine/war3work/Daemonic Sword ORPG 6.79/map/scripts/war3map.j"
    main(file_path)
