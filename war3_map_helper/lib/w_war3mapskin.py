import q
import re
# import configparser
from lib import MyReader


class Worker(object):
    """
        docstring for Worker
    """
    WORK_ITEM = ["Nolumber", "BONUS_DAMAGE", "COLON_LUMBER", "IDLE_PEON", "IDLE_PEON_DESC", "ITEM_PAWN_TOOLTIP", "ITEM_USE_TOOLTIP", "KEY_QUESTS", "LUMBER", "QUESTS", "QUESTSMAIN", "QUESTSOPTIONAL", "UPPER_BUTTON_QUEST_TIP"]
    # WORK_ITEM = [x.lower() for x in WORK_ITEM]
    WORK_ITEM = set([x.lower() for x in WORK_ITEM])
    # SKIP_ITEM = {
    #     "CustomSkin": [
    #         ".*"
    #     ],
    #     "Errors": [
    #         ""
    #     ],
    #     "FrameDef": [
    #         "RESOURCE_UBERTIP_GOLD", "RESOURCE_UBERTIP_LUMBER", "RESOURCE_UBERTIP_UPKEEP", "RESOURCE_UBERTIP_UPKEEP_INFO", "RESOURCE_UBERTIP_UPKEEP_INFO_WOOD",
    #         "UPKEEP_HIGH", "UPKEEP_LOW", "UPKEEP_NONE",
    #     ],
    # }

    def __init__(self, arg):
        super(Worker, self).__init__()
        self.arg = arg
        # self.arg["config"] = configparser.RawConfigParser()
        self.arg["config"] = MyReader(self.arg["file_path"])
        # self.arg["config"].read(self.arg["file_path"])

        # for sect in self.SKIP_ITEM:
        #     self.SKIP_ITEM[sect] = "|".join(self.SKIP_ITEM[sect])

    def grep_string_from_config(self):
        string_list = []
        for sect_key in self.arg["config"]:
            section = self.arg["config"][sect_key]
            for item_key in section:
                # item_key 会被转化为全小写
                # if re.match(self.SKIP_ITEM[sect_key], item_key, flags=re.I):
                #     continue

                if item_key.lower() in self.WORK_ITEM:
                    string_list.append(section[item_key])

        return string_list
