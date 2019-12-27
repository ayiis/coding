import q
import re
# import configparser
from lib import MyReader


class Worker(object):
    """
        docstring for Worker
    """
    WORK_ITEM = [
        "Nolumber", "BONUS_DAMAGE", "COLON_LUMBER", "IDLE_PEON", "IDLE_PEON_DESC",
        "ITEM_PAWN_TOOLTIP", "ITEM_USE_TOOLTIP", "KEY_QUESTS", "LUMBER", "QUESTS",
        "QUESTSMAIN", "QUESTSOPTIONAL", "UPPER_BUTTON_QUEST_TIP",
        "ARMORTIP_DIVINE", "ARMORTIP_DIVINE_V0C", "ARMORTIP_DIVINE_V0M", "COLON_GOLD_INCOME_RATE",
        "DAMAGETIP_CHAOS", "DAMAGETIP_CHAOS_V0C", "DAMAGETIP_CHAOS_V0M", "RESOURCE_UBERTIP_GOLD",
        "RESOURCE_UBERTIP_LUMBER", "RESOURCE_UBERTIP_UPKEEP", "RESOURCE_UBERTIP_UPKEEP_INFO", "UPKEEP_NONE",
        "UndeadClass",
        "ARMORTIP_FORT", "ARMORTIP_FORT_V0C", "ARMORTIP_FORT_V0M", "ARMORTIP_MEDIUM", "ARMORTIP_MEDIUM_V0M",
        "ARMORTIP_NONE", "ARMORTIP_NONE_V0C", "ARMORTIP_NONE_V0M", "ARMORTIP_NORMAL", "ARMORTIP_SMALL",
        "ARMORTIP_SMALL_V0C", "ARMORTIP_SMALL_V0M", "ARMOR_FORT", "ARMOR_NONE", "ARMOR_NORMAL", "ARMOR_SMALL",
        "DAMAGETIP_MAGIC", "DAMAGETIP_MAGIC_V0C", "DAMAGETIP_MAGIC_V0M", "DAMAGETIP_MELEE",
        "DAMAGETIP_MELEE_V0C", "DAMAGETIP_MELEE_V0M", "DAMAGETIP_NORMAL", "DAMAGETIP_NORMAL_V0C",
        "DAMAGETIP_NORMAL_V0M", "DAMAGETIP_PIERCE", "DAMAGETIP_PIERCE_V0C", "DAMAGETIP_PIERCE_V0M",
        "DAMAGETIP_SIEGE", "DAMAGETIP_SIEGE_V0C", "DAMAGETIP_SIEGE_V0M", "DAMAGE_MAGIC", "DAMAGE_MELEE",
        "DAMAGE_NORMAL", "DAMAGE_PIERCE", "DAMAGE_SIEGE"
    ]
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
