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
        "DAMAGE_NORMAL", "DAMAGE_PIERCE", "DAMAGE_SIEGE",
        "Absorbmana", "Nomana", "UnitHPmaxed", "ALLIANCES", "ALLIES", "COLON_FOOD", "COLON_FOOD_PROVIDED",
        "COLON_FOOD_TOTAL", "COLON_FOOD_USED", "COLON_GOLD", "COLON_HUMAN", "COLON_ORC", "COLON_PROVIDED",
        "COLON_UNDEAD", "CONTINUE_PLAYING", "DAMAGE_CHAOS", "GAMEOVER_CONTINUE_GAME", "GAMEOVER_GAME_OVER",
        "GAMEOVER_NEUTRAL", "GOLD", "HUMAN", "INTELLECT_HILIGHT", "KEY_ALLIES", "ORC",
        "PAUSE_GAME_NOTIFY_NO_TIMEOUT", "RESOURCES_COLUMN0", "RESOURCE_UBERTIP_SUPPLY", "RESUME_GAME_NOTIFY",
        "UNDEAD", "UPPER_BUTTON_ALLY_TIP",
        "ARMORTIP_HERO", "ARMORTIP_HERO_V0C", "ARMORTIP_HERO_V0M", "ARMORTIP_LARGE", "ARMORTIP_LARGE_V0C", "ARMORTIP_LARGE_V0M", "ARMORTIP_NORMAL_V0M",
        "Cooldownstock", "Notancient", "Notpowerup", "Notsapper", "Outofstock", "Upkeeplevel",
        "ARMOR_DIVINE", "ARMOR_MEDIUM",
        "COLON_FOOD_MAX", "COLON_HERO_ATTRIBUTES", "COLON_MOVE_SPEED", "COLON_SPEED", "COLON_UPKEEP", "COMPUTER_INSANE", "COMPUTER_NEWBIE", "COMPUTER_NORMAL",
        "DAMAGETIP_HERO", "DAMAGETIP_HERO_V0C", "DAMAGETIP_HERO_V0M",
        "GAMEOVER_QUIT_GAME", "GAMEOVER_QUIT_MISSION", "PLAYER_LEFT_GAME", "REQUIREDLEVELTOOLTIP", "RESOURCE_UBERTIP_UPKEEP_INFO_WOOD", "SPEED",
        "UPKEEP_HIGH", "UPKEEP_HIGH2", "UPKEEP_HIGH3", "UPKEEP_HIGH4", "UPKEEP_HIGH5", "UPKEEP_HIGH6", "UPKEEP_HIGH7", "UPKEEP_HIGH8", "UPKEEP_LOW",
        "UPPER_BUTTON_CHAT_UBER",

        "HPmaxed", "Manamaxed", "Nogold", "Notinrange", "Notinvulnerable", "UnderRange", "UnitManaMaxed", "AGILITY_HILIGHT",
        "ARMORTIP_MEDIUM_V0C", "ARMORTIP_NORMAL_V0C", "ARMOR_HERO", "ARMOR_LARGE", "CHAT_RECIPIENT_PRIVATE", "CHEATDISABLED", "CHEATENABLED", "COLON_ARMOR", "COLON_DAMAGE",

        "CONFIRM_EXIT", "CONFIRM_EXIT_MESSAGE", "DAMAGE_HERO", "DISCONNECT", "END_GAME", "GAMEOVER_DEFEAT_MSG", "GAMEOVER_VICTORY", "INVULNERABLE", "KEY_CANCEL",

        "KEY_END_GAME", "KEY_EXIT", "KEY_EXIT_PROGRAM", "KEY_PAUSE_GAME", "KEY_QUIT", "KEY_QUIT_MISSION", "KEY_SAVE_GAME", "LOADING_LOADING", "LOADING_WAITING_FOR_PLAYERS", "MOVESPEEDAVERAGE", "OVERVIEW_COLUMN1", "QUIT", "QUIT_MISSION", "RESOURCES_COLUMN1", "SCORESCREEN_TAB2", "STRENGTH_HILIGHT", "WAITING_FOR_HOST", "WAITING_FOR_PLAYERS",


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
