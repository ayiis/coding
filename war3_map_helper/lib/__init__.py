"""
    w3x2lni 自定义了一些 ini 结构，不能直接用 python 自带的库 configparser 读取
    这里直接自己写方法读取 (只用于兼容 w3x2lni 的数据结构)
"""
import q
import re
import traceback


class BaseWorker(object):

    WORK_ITEM = set([])

    def __init__(self, arg):
        super(BaseWorker, self).__init__()
        self.arg = arg
        self.arg["config"] = MyReader(self.arg["file_path"])
        self.WORK_ITEM = set([x.lower() for x in self.WORK_ITEM])

    def get_deep_string_from_list(self, item_list):
        res = []
        if isinstance(item_list, list):
            for item in item_list:
                res += self.get_deep_string_from_list(item)
                # if isinstance(item, list):
                #     res += self.get_deep_string_from_list(item)
        else:
            res.append(item_list)

        return res

    def grep_string_from_config(self):
        string_list = []
        for sect_key in self.arg["config"]:
            section = self.arg["config"][sect_key]
            for item_key in section:
                # print("section[item_key]:", section[item_key])
                if item_key.lower() in self.WORK_ITEM:
                    zzz = self.get_deep_string_from_list(section[item_key])
                    string_list += zzz

                    # "Увеличение запаса здоровья рыцарей, ястребов и грифонов на <Rhan,base2> ед.",\n'
                    # if "Увеличение запаса здоровья рыцарей" in section[item_key]:
                    #     q.d()
                    #     exit()

        # print("string_list:", string_list)
        # q.d()
        # exit()
        return string_list


def MyReader(file_path):

    ini_obj = {}
    with open(file_path, "r") as rf:
        wait_end = False
        sect_name = None
        key_name = None
        wait_string = False
        start_debug = False
        wait_string2 = False
        w_index = 0
        for lineno, line in enumerate(rf):

            # 兼容平台换行格式
            while line[-1:] == "\n":
                line = line[:-1]

            try:

                # if not start_debug and sect_name == "A00B" and key_name == "Ubertip":
                #     start_debug = True

                # if start_debug:
                #     q.d()

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
                        ini_obj[sect_name][key_name].append(append_string)

                    continue

                # 如果在跨行字符串 -> 对象
                if wait_end:

                    # 如果遇到跨行字符串
                    if wait_string2:
                        append_string = line

                        if line.strip()[-3:] == "]=]":
                            wait_string2 = False
                            append_string = line.strip()[:-3].strip()
                        elif line.strip()[-4:] == "]=],":
                            wait_string2 = False
                            append_string = line.strip()[:-4].strip()

                        if append_string:
                            # ini_obj[sect_name][key_name].append(append_string)
                            ini_obj[sect_name][key_name][w_index].append(append_string)

                        continue

                    # 判断对象是否完结
                    if line.strip() == "}":
                        wait_end = False
                        key_name = None
                    elif line[-3:] == "[=[":
                        wait_string2 = True
                        w_index = len(ini_obj[sect_name][key_name])
                        ini_obj[sect_name][key_name].append([])
                    else:
                        ini_obj[sect_name][key_name].append(line)

                    continue

                else:
                    line = line.strip()
                    # 无视注释和空行
                    if not line or line[:2] == "--":
                        continue

                # 判断值是否对象
                if line[-1:] == "{":
                    wait_end = True
                    key_name = line.split("=")[0].strip()
                    ini_obj[sect_name][key_name] = []
                elif line[-3:] == "[=[":
                    wait_string = True
                    key_name = line.split("=")[0].strip()
                    ini_obj[sect_name][key_name] = []

                # 判断是否新节点
                # 未兼容 单行 [=[ 和 ]=] 同时存在的情况
                elif re.match(r"^\[([a-z0-9]+)\]$", line, re.I):
                    sect_name = re.match(r"^\[([a-z0-9]+)\]$", line, re.I).group(1)
                    ini_obj[sect_name] = {}
                    # print("Add new section: [%s]" % sect_name)

                # 直接赋值
                elif "=" in line:
                    key_name = line.split("=")[0]
                    key_val = line[len(key_name) + 1:]
                    key_name = key_name.strip()
                    ini_obj[sect_name][key_name] = key_val.strip()

                else:
                    raise Exception("[CANNOT PARSE]")

            except Exception:
                print(traceback.format_exc())
                q.d()

    # print(
    #     "ini_obj['A00B']['Ubertip']:",
    #     ini_obj['A00B']['Tip'],
    #     ini_obj['A00B']['Ubertip']
    # )
    # q.d()
    # exit(1)
    # if "table/upgrade.ini" in file_path:
    #     q.d()

    return ini_obj


def test():
    rr = MyReader("/mine/war3work/(2)Game of Life and Death-v2/table/ability.ini")
    print("rr:", rr)


if __name__ == "__main__":
    test()
    # ini_obj["A002"]["Ubertip"]
