import q
import re
from lib import BaseWorker


class AbilityWorker(BaseWorker):
    WORK_ITEM = ["Ubertip", "Unubertip", "Untip", "Tip", "Researchtip", "Researchubertip", "EditorSuffix", "Name"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class BuffWorker(BaseWorker):
    WORK_ITEM = ["Bufftip", "Buffubertip", "EditorName", "EditorSuffix"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class DestructableWorker(BaseWorker):
    WORK_ITEM = ["Name", "EditorSuffix"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class DoodadWorker(BaseWorker):
    WORK_ITEM = ["Name", "EditorSuffix"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class ItemWorker(BaseWorker):
    WORK_ITEM = ["Ubertip", "Description", "Ubertip", "Name", "Tip", "EditorSuffix"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class UnitWorker(BaseWorker):
    WORK_ITEM = ["Propernames", "Name", "Tip", "Ubertip", "EditorSuffix", "Description"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class UpgradeWorker(BaseWorker):
    WORK_ITEM = ["Propernames", "Name", "Tip", "Ubertip", "EditorSuffix"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class W3iWorker(BaseWorker):
    WORK_ITEM = ["地图描述", "文本", "标题", "子标题", "名字", "队伍名称", "物品列表名称"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class CommandStringsWorker(BaseWorker):
    WORK_ITEM = [
        "Tip", "Ubertip", "Emptycontrolgroup", "Invalidcontrolgroup", "Itemincontrolgroup",
        "Nofood", "Maxsupply", "Nogold", "Nolumber", "Nomana", "Cooldown", "Noroom",
        "Canttransport", "Cantdevour", "Cantcyclone", "Cantspiritwolf", "Cantpossess",
        "Onlyattackers", "Notentangledmine", "Notblightedmine", "Alreadyentangled",
        "Alreadyblightedmine", "Targetwispresources", "Targetblightedmine", "Entangleminefirst",
        "Blightminefirst", "Entangledminefull", "Blightringfull", "Acolytealreadymining",
        "Nototherplayersmine", "Targgetmine", "Targgetresources", "Humanbuilding",
        "Undeadbuilding", "Underconstruction", "Alreadyrebuilding", "Creeptoopowerful",
        "Hibernating", "Immunetomagic", "Holybolttarget", "Deathcoiltarget", "Dispelmagictarget",
        "Treeoccupied", "Coupletarget", "Mounthippogryphtarget", "Archerridertarget", "Cantsee",
        "Cantplace", "Outofbounds", "Offblight", "Tooclosetomine", "Tooclosetohall",
        "Buildingblocked", "Teleportfail", "Stumpblocked", "Cantland", "Cantroot", "Cantrootunit",
        "Mustroottoentangle", "Mustbeclosertomine", "Minenotentangleable", "Notinrange",
        "UnderRange", "Notthisunit", "Targetunit", "Targetstructuretree", "Targetground",
        "Targetair", "Targetstructure", "Targetward", "Targetitem", "Targettree", "Targetrepair",
        "Targetowned", "Targetally", "Targetneutral", "Targetenemy", "Targethero", "Targetenemyhero",
        "Targetcorpse", "Targetfleshycorpse", "Targetbonecorpse", "Targetundead", "Targetmechanical",
        "Targetmoveable", "Targetorganicground", "Targetancient", "Targetarmoredtransport",
        "Targetmanauser", "Targetbunkerunit", "Targetwisp", "Targetacolyte", "Targetpit",
        "Needemptytree", "Cantfindcorpse", "Cantfindfriendlycorpse", "Nounits", "Noground",
        "Noair", "Nostructure", "Noward", "Noitem", "Notree", "Nowall", "Nodebris", "Notfrozenbldg",
        "Nottownhall", "Notself", "Notowned", "Notfriendly", "Notneutral", "Notenemy", "Nothidden",
        "Notinvulnerable", "Nohero", "Notcorpse", "Notfleshycorpse", "Notbonecorpse", "Notmechanical",
        "Notorganic", "Notdisabled", "Cantattackloc", "Canttargetloc", "Inventoryfull", "NeedInventory",
        "Notsapper", "Notancient", "Notsummoned", "Nottransport", "Notunsummoned", "Notillusion",
        "Notmorphing", "Notdot", "Illusionscantharvest", "Illusionscantpickup", "Cantpolymorphunit",
        "Notundead", "Heromaxed", "HPmaxed", "Manamaxed", "HPmanamaxed", "UnitHPmaxed", "RepairHPmaxed",
        "Alreadybeinghealed", "Pitalreadysacrificing", "Outofstock", "Cooldownstock", "Cantdrop",
        "Calltoarms", "Backtowork", "BattleStations", "Unitattack", "Townattack", "Herodies",
        "Allyunderattack", "Allytownattack", "Allyminimapping", "Goldandlumberfromally", "Goldfromally",
        "Lumberfromally", "Goldminedestroyed", "Upkeeplevel", "Herokilledhero", "Herodeath",
        "Goldminelow", "Controlgranted", "Controlrevoked"
    ]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]
