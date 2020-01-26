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
}


CATCH_PLE = {
    "[": ["[", "]"],
    "(": ["(", ")"],
}


def translate(word):
    print("[translate]", word.replace("\n", "\\n"))
    return "\"*AY_STRING_HERE\""

    # return word


def loop_obj(obj, p, name, i):

    # This is the para of string
    if type(obj) is list and name in WORK_ITEM and i in LINE_PLACE[name][:-1]:

        re2 = []
        # q.d()
        # if type(obj) is dict:
        for item in obj:
            # q.d()
            if type(item) is str and item[0] == "\"":
                re2.append(translate(item))
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
        # try:
        #     return p.join([((item and item[0] == "\"") and translate(item) or item) for item in obj])
        # except Exception as e:
        #     print("".join(traceback.format_stack()))
        #     q.d()

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


if __name__ == '__main__':

    # para_list = {'DisplayTextToForce': [['('], [{'GetForceOfPlayer': [['('], [{'GetOwningPlayer': [['('], [{'GetTriggerUnit': [['('], []]}]]}]]}], [{'': [['('], ['"|cffFF0000 Experience Lost: |r"', '+', {'I2S': [['('], ['udg_Generic_Integer']]}]]}]]}

    # ree = loop_obj(para_list, ", ", "", 0)

    # print("ree:", ree)
    "\x00"

    rstring = r"(\\[trn]|[\t\n\r]|(\|[rn])?\-[a-z0-9]+|http[s]?\:\/\/[^\ \"\'\|]+|\<[a-z0-9]{4}(\:[a-z0-9]{4})?,[a-z0-9]+\>|TRIGSTR_[0-9]+|\%[a-z]\b|\|c[0-9a-f]{8}|[0-9\+\-\%]|\|n|\|r|[\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\:\"\,\.\/\<\>\?“”])"

    x = "|c003399ffAuto-Select Skills:|r -pickskills|c003399ffSave: |r-save"
    sentence = x
    print("x:", x)
    # temp = re.sub(rstring, "*", sentence, flags=re.I)
    # print(temp)

    tmp_group = []
    def fff(m):
        tmp_group.append(m.group(0))
        return "\x00"

    def rrr(m):
        return " 《" + tmp_group.pop() + "》 "
        # return tmp_group.pop()

    ttt = re.sub(rstring, fff, sentence)
    print(ttt)
    print()
    tmp_group.reverse()
    ttt = re.sub(r"[\0]", rrr, ttt)
    print(ttt)
    print()
    assert ttt == x, "NO!"
    q.d()


