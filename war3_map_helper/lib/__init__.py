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

        # # !!!!
        # if "name" in self.WORK_ITEM:
        #     self.WORK_ITEM.remove("name")

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
    with open(file_path, "rb") as rf:
        contents_tmp = rf.readlines()
        contents = []
        i = 0
        for c in contents_tmp:
            i = i + 1

            # if i >= 34700:
            #     # наносящее его противникам по
            #     q.d()

            # w3x2lni cannot handle (\xd0, \xd1)
            if c[-4:] in (b"\xd0\"\r\n", b"\xd1\"\r\n"):
                print("Line", i, "is bad char")
                c = c[:-4] + b" \"\r\n"
            else:
                pass

            try:
                contents.append(c.decode("utf8"))
            except Exception as e:
                print(e, "is bad char")
                q.d()

            # if "наносящее его противникам по" in contents[-1]:
            #     print("in the MyReader")
            #     q.d()

        wait_end = False
        sect_name = None
        key_name = None
        wait_string = False
        # start_debug = False
        wait_string2 = False
        w_index = 0
        for lineno, line in enumerate(contents):

            # 兼容平台换行格式
            while line[-1:] == "\n":
                line = line[:-1]
            while line[:1] == "\ufeff":
                line = line[1:]

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

                # if file_path == "/mine/war3work/Otro Mapa TD de Warcraft III/map/Units/CommandStrings.txt":
                #     q.d()

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
                elif re.match(r"^\[([a-z0-9]{4})\]$", line, re.I):
                    sect_name = re.match(r"^\[([a-z0-9]{4})\]$", line, re.I).group(1)
                    ini_obj[sect_name] = {}
                    # print("Add new section: [%s]" % sect_name)
                elif re.match(r"^\[([^\[\]\"\']+)\]$", line, re.I):
                    print("warn:", "Be not 'abcd' type ID:", line)
                    sect_name = re.match(r"^\[([^\[\]\"\']+)\]$", line, re.I).group(1)
                    ini_obj[sect_name] = {}
                elif re.match(r"^\[(.+)\]$", line, re.I):
                    print("warn:", "Very bad [\"\\\\I0F\"] type ID:", line)
                    sect_name = re.match(r"^\[(.+)\]$", line, re.I).group(1)
                    ini_obj[sect_name] = {}
                # 直接赋值
                elif "=" in line:
                    key_name = line.split("=")[0]
                    key_val = line[len(key_name) + 1:]
                    key_name = key_name.strip()
                    ini_obj[sect_name][key_name] = key_val.strip()

                else:
                    print("[!CANNOT PARSE]", line)
                    # raise Exception("[CANNOT PARSE]")

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


def format_str(string):
    string = re.sub(r"\|c[a-zA-Z0-9]{8}", "", string, flags=re.I)
    string = re.sub(r"\|r", "", string, flags=re.I)
    string = re.sub(r"\|n", ", ", string, flags=re.I)

    return string


def test():
    # rr = MyReader("/mine/war3work/(2)Game of Life and Death-v2/table/ability.ini")
    # rr = MyReader("/mine/war3work/PatisauR's ORPG 1/table/item.ini")
    # rr = MyReader("/mine/war3work/Daemonic Sword ORPG 6.79/table/item.ini")
    rr = MyReader("/mine/war3work/Daemonic Sword ORPG 6.79/table/unit.ini")
    # print("rr:", rr)
    for key in rr:
        item = rr[key]
        if "公主" in item.get("Name", ""):
            print(item)
            print()

    exit()
    rrr = []
    for x in rr:
        rr[x]["id"] = x
        rrr.append(rr[x])
    print(len(rrr))
    rrr = filter(lambda x: int(x.get("Level") or "0") >= 350 and "最终" not in x.get("Name", ""), rrr)
    rrr = list(rrr)
    print(len(rrr))
    rrr.sort(key=lambda x: -int(x.get("Level") or "0"))
    print(len(rrr))
    cgood = 0
    for item in rrr:
        lv = item.get("Level")
        if "精美" not in item.get("Name", ""):
            continue
        print(lv, item)
        print()
        if "Description" in item and "Ubertip" in item:
            good = False
            content = ""
            if "必填项" in item.get("Description", ""):
                good = True
                content = item.get("Description")
            if "必填项" in item.get("Ubertip", ""):
                good = True
                content = item.get("Ubertip")

            if good:
                cgood += 1
                print(format_str(item.get("Name", "")), "说明：", format_str(content))
                print()

    print("cgood:", cgood)


if __name__ == "__main__":
    test()
    # ini_obj["A002"]["Ubertip"]
