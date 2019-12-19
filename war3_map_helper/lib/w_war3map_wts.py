import q
import re


class Worker(object):
    """
        docstring for Worker
    """
    WORK_ITEM = ["Nolumber", "BONUS_DAMAGE", "COLON_LUMBER", "IDLE_PEON", "IDLE_PEON_DESC", "ITEM_PAWN_TOOLTIP", "ITEM_USE_TOOLTIP", "KEY_QUESTS", "LUMBER", "QUESTS", "QUESTSMAIN", "QUESTSOPTIONAL", "UPPER_BUTTON_QUEST_TIP"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]

    def __init__(self, arg):
        super(Worker, self).__init__()
        self.arg = arg

    def grep_string_from_config(self):
        string_list = []
        with open(self.arg["file_path"], "r") as rf:
            contents = rf.readlines()
        wts_obj = {}
        key_index = None
        wait_line1 = False
        wait_line2 = False
        for lineno, rawline in enumerate(contents):
            line = rawline

            # 兼容平台换行格式
            while line[-1:] == "\n":
                line = line[:-1]

            if wait_line2:
                if line == "}":
                    wait_line2 = False
                    continue

                wts_obj[key_index].append(rawline)
            elif wait_line1:
                if line == "{":
                    wait_line1 = False
                    wait_line2 = True
                    continue
            else:
                if re.match(r"^STRING [\d]+$", line, flags=re.I):
                    key_index = re.match(r"^STRING ([\d]+)$", line, flags=re.I).group(1)
                    wts_obj[key_index] = []
                    wait_line1 = True
                    continue

        for i in wts_obj:
            string_list += wts_obj[i]

        return string_list


def test():
    wk = Worker({
        "file_path": "/mine/war3work/(2)Game of Life and Death-v2/map/war3map.wts"
    })
    string_list = wk.grep_string_from_config()
    print("string_list:", string_list)


if __name__ == "__main__":
    test()
