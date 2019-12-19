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
    WORK_ITEM = ["Propernames", "Name", "Tip", "EditorSuffix"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]


class UpgradeWorker(BaseWorker):
    WORK_ITEM = ["Propernames", "Name", "Tip", "Ubertip", "EditorSuffix"]
    WORK_ITEM = [x.lower() for x in WORK_ITEM]