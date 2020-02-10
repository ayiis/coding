import q
import os
import shutil
from pathlib import Path
from worker import ini_work_files, slk_work_files, wts_work_files, jass_work_files
from worker import TranslateWorkerForIni, TranslateWorkerForWts, TranslateWorkerForJ


class StartWork(object):
    """
        start from the begin
    """
    def __init__(self, arg):
        super(StartWork, self).__init__()
        self.arg = arg
        self.from_lan = arg["from_lan"]
        self.target_dir = arg["target_dir"]
        if not Path("./data/").is_dir():
            os.mkdir("./data/")

    def do_ini(self):

        self.tw_ini = TranslateWorkerForIni({
            "target_dir": self.target_dir
        })
        self.tw_ini.grep_ini()
        text_set = list(set(self.tw_ini.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        self.tw_ini.restruct_strings()
        # print("sentence_set:", self.tw_ini.sentence_set)
        print("sentence_set:", len(self.tw_ini.sentence_set))

        self.tw_ini.do_translate("test", "ru", "zh")
        # self.tw_ini.do_translate("baidu", "ru", "zh")
        # print("trans_result:", self.tw_ini.trans_result)
        print("trans_result:", len(self.tw_ini.trans_result))

        self.tw_ini.rewrite_ini()

    def do_wts(self):
        self.tw_wts = TranslateWorkerForWts({
            "target_dir": self.target_dir
        })
        self.tw_wts.grep_wts()

        text_set = list(set(self.tw_wts.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        self.tw_wts.restruct_strings()
        print("sentence_set:", len(self.tw_wts.sentence_set))

        self.tw_wts.do_translate("test", "ru", "zh")
        # self.tw_wts.do_translate("baidu", "ru", "zh")
        print("trans_result:", len(self.tw_wts.trans_result))

        self.tw_wts.rewrite_wts()

    def do_j(self):

        self.tw_j = TranslateWorkerForJ({
            "target_dir": self.target_dir
        })
        self.tw_j.grep_j()

        text_set = list(set(self.tw_j.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        self.tw_j.restruct_strings()
        print("sentence_set:", len(self.tw_j.sentence_set))

        self.tw_j.do_translate("test", "ru", "zh")
        # self.tw_j.do_translate("baidu", "ru", "zh")
        print("trans_result:", len(self.tw_j.trans_result))

        self.tw_j.rewrite_j()

    def do_check_result(self):
        """
            意义不大
            目前只开放给 俄语
        """
        # 翻译完成后，检查所有文件是否还含有俄文字母
        eee = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "ъ", "ы", "ь", "Э", "Ю", "Я"]
        eee += [x.lower() for x in eee]
        eee = list(set(eee))
        self.tw_ini.check_result(eee, ini_work_files)
        self.tw_wts.check_result(eee, wts_work_files)
        self.tw_j.check_result(eee, jass_work_files)

    def _move_file(self, file_name):
        file_path = "%s/%s" % (self.target_dir, file_name)
        if not Path(file_path).is_file():
            return
        new_file_path = "%s.mta2.cache" % file_path
        bak_file_path = "%s.bak" % file_path
        shutil.move(file_path, bak_file_path)
        shutil.move(new_file_path, file_path)

    def do_move_file(self):

        for file_name in ini_work_files:
            self._move_file(file_name)

        for file_name in slk_work_files:
            self._move_file(file_name)

        for file_name in wts_work_files:
            self._move_file(file_name)

        for file_name in jass_work_files:
            self._move_file(file_name)


def test_ru():

    # 翻译完成后，检查所有文件是否还含有俄文字母
    eee = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "ъ", "ы", "ь", "Э", "Ю", "Я"]
    eee += [x.lower() for x in eee]
    eee = list(set(eee))

    if not Path("./data/").is_dir():
        os.mkdir("./data/")

    arg = {
        # "target_dir": "/mine/war3work/(2)Game of Life and Death-v2/",
        # "target_dir": "/mine/war3work/OpenHero_0_99j_ENG",
        # "target_dir": "/mine/war3work/Schizophrenia 1.23.10",
        "target_dir": "/mine/war3work/Paranormal_Underworld_ORPG_Final_L",
    }

    # if False:
    if True:
        tw = TranslateWorkerForIni(arg)
        tw.grep_ini()
        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        # print("sentence_set:", tw.sentence_set)
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "ru", "zh")
        # tw.do_translate("baidu", "ru", "zh")
        # print("trans_result:", tw.trans_result)
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_ini()

        # tw.do_check_result()

    # if False:
    if True:
        tw = TranslateWorkerForWts(arg)
        tw.grep_wts()

        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "ru", "zh")
        # tw.do_translate("baidu", "ru", "zh")
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_wts()

        # tw.check_result(eee)

    # if False:
    if True:
        tw = TranslateWorkerForJ(arg)
        tw.grep_j()

        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "ru", "zh")
        # tw.do_translate("baidu", "ru", "zh")
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_j()

        # tw.check_result(eee)

    # if False:
    if True:

        def move_file(file_name):
            file_path = "%s/%s" % (arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                return
            new_file_path = "%s.mta2.cache" % file_path
            bak_file_path = "%s.bak" % file_path
            shutil.move(file_path, bak_file_path)
            shutil.move(new_file_path, file_path)

        for file_name in ini_work_files:
            move_file(file_name)

        for file_name in slk_work_files:
            move_file(file_name)

        for file_name in wts_work_files:
            move_file(file_name)

        for file_name in jass_work_files:
            move_file(file_name)

    # 删除 bak 文件
    # if False:
    if True:

        def delete_file(file_name):
            file_path = "%s/%s" % (arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                return

            bak_file_path = "%s.bak" % file_path
            # shutil.delete(bak_file_path)
            os.remove(bak_file_path)

        for file_name in ini_work_files:
            delete_file(file_name)

        for file_name in slk_work_files:
            delete_file(file_name)

        for file_name in wts_work_files:
            delete_file(file_name)

        for file_name in jass_work_files:
            delete_file(file_name)


def test_en():

    # # 翻译完成后，检查所有文件是否还含有俄文字母
    # eee = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "ъ", "ы", "ь", "Э", "Ю", "Я"]
    # eee += [x.lower() for x in eee]
    # eee = list(set(eee))

    if not Path("./data/").is_dir():
        os.mkdir("./data/")
    else:
        pass

    arg = {
        # "target_dir": "/mine/war3work/Wintermaul_One_Revolution_v1.3/",
        # "target_dir": "/mine/war3work/PatisauR's ORPG 1/",
        # "target_dir": "/mine/war3work/Justice of Shadow 1.0/",
        # "target_dir": "/mine/war3work/opt-The Black Road v1.2/",
        # "target_dir": "/mine/war3work/Daemonic Sword ORPG 6.79/",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/prologue - the chosen ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/epilogue",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 1 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 2 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 3 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 4 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 5 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 6 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 7 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 8 - the chones ones campaign",
        # "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 9 - the chosen ones campaign",
        "target_dir": "/mine/war3work/The-Chosen-Ones-1.0_x/map/chapter 10 - the chosen ones campaign",
    }
    debugs = {
        "ini": True,
        "wts": True,
        "j": True,
        "movefile": True,
        "delbak": True,
    }

    if debugs.get("ini"):
        tw = TranslateWorkerForIni(arg)
        tw.grep_ini()
        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        # print("sentence_set:", tw.sentence_set)
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "en", "zh")
        # tw.do_translate("baidu", "en", "zh")
        # print("trans_result:", tw.trans_result)
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_ini()

        # tw.check_result(eee)  # 英文暂时不能check
    if debugs.get("wts"):
        tw = TranslateWorkerForWts(arg)
        tw.grep_wts()

        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "en", "zh")
        # tw.do_translate("baidu", "en", "zh")
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_wts()

        # tw.check_result(eee)  # 英文暂时不能check
    if debugs.get("j"):
        tw = TranslateWorkerForJ(arg)
        tw.grep_j()

        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "en", "zh")
        # tw.do_translate("baidu", "en", "zh")
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_j()

        # tw.check_result(eee)  # 英文暂时不能check

    # 写进原文件
    if debugs.get("movefile"):

        def move_file(file_name):
            file_path = "%s/%s" % (arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                return

            new_file_path = "%s.mta2.cache" % file_path
            bak_file_path = "%s.bak" % file_path
            shutil.move(file_path, bak_file_path)
            shutil.move(new_file_path, file_path)

        for file_name in ini_work_files:
            move_file(file_name)

        for file_name in slk_work_files:
            move_file(file_name)

        for file_name in wts_work_files:
            move_file(file_name)

        for file_name in jass_work_files:
            move_file(file_name)

    # 删除 bak 文件
    if debugs.get("delbak"):

        def delete_file(file_name):
            file_path = "%s/%s" % (arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                return

            bak_file_path = "%s.bak" % file_path
            # shutil.delete(bak_file_path)
            os.remove(bak_file_path)

        for file_name in ini_work_files:
            delete_file(file_name)

        for file_name in slk_work_files:
            delete_file(file_name)

        for file_name in wts_work_files:
            delete_file(file_name)

        for file_name in jass_work_files:
            delete_file(file_name)


def test_es():

    if not Path("./data/").is_dir():
        os.mkdir("./data/")
    arg = {
        # "target_dir": "/mine/war3work/Wintermaul_One_Revolution_v1.3/",
        # "target_dir": "/mine/war3work/PatisauR's ORPG 1/",
        "target_dir": "/mine/war3work/ArtededefensaV4.7/",
    }

    # if False:
    if True:
        tw = TranslateWorkerForIni(arg)
        tw.grep_ini()
        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        # print("sentence_set:", tw.sentence_set)
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "es", "zh")
        # tw.do_translate("baidu", "es", "zh")
        # print("trans_result:", tw.trans_result)
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_ini()

        # tw.check_result(eee)  # 英文暂时不能check
    # if False:
    if True:
        tw = TranslateWorkerForWts(arg)
        tw.grep_wts()

        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "es", "zh")
        # tw.do_translate("baidu", "es", "zh")
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_wts()

        # tw.check_result(eee)  # 英文暂时不能check
    # if False:
    if True:
        tw = TranslateWorkerForJ(arg)
        tw.grep_j()

        text_set = list(set(tw.text_cache))
        # print("text_set:", text_set)
        print("Count in set:", len(text_set))

        tw.restruct_strings()
        print("sentence_set:", len(tw.sentence_set))

        tw.do_translate("test", "es", "zh")
        # tw.do_translate("baidu", "es", "zh")
        print("trans_result:", len(tw.trans_result))

        tw.rewrite_j()

        # tw.check_result(eee)  # 英文暂时不能check

    if False:
    # if True:

        def move_file(file_name):
            file_path = "%s/%s" % (arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                print("[EMPTY]", file_path)
                return

            new_file_path = "%s.mta2.cache" % file_path
            bak_file_path = "%s.bak" % file_path
            shutil.move(file_path, bak_file_path)
            shutil.move(new_file_path, file_path)

        for file_name in ini_work_files:
            move_file(file_name)

        for file_name in slk_work_files:
            move_file(file_name)

        for file_name in wts_work_files:
            move_file(file_name)

        for file_name in jass_work_files:
            move_file(file_name)

    # 删除 bak 文件
    if False:
    # if True:

        def delete_file(file_name):
            file_path = "%s/%s" % (arg["target_dir"], file_name)
            if not Path(file_path).is_file():
                return

            bak_file_path = "%s.bak" % file_path
            # shutil.delete(bak_file_path)
            os.remove(bak_file_path)

        for file_name in ini_work_files:
            delete_file(file_name)

        for file_name in slk_work_files:
            delete_file(file_name)

        for file_name in wts_work_files:
            delete_file(file_name)

        for file_name in jass_work_files:
            delete_file(file_name)


if __name__ == "__main__":
    # test_ru()
    test_en()
    # test_es()
    # test_vi()

    # arg = {
    #     # "target_dir": "/mine/war3work/Wintermaul_One_Revolution_v1.3/",
    #     # "target_dir": "/mine/war3work/PatisauR's ORPG 1/",
    #     # "target_dir": "/mine/war3work/ArtededefensaV4.7/",
    #     "target_dir": "/mine/war3work/Daemonic Sword ORPG 6.79/",
    # }
    # tw = TranslateWorkerForJ(arg)
    # tw.grep_j()

    # text_set = list(set(tw.text_cache))
    # # print("text_set:", text_set)
    # print("Count in set:", len(text_set))

    # tw.restruct_strings()
    # print("sentence_set:", len(tw.sentence_set))

    # tw.do_translate("test", "vi", "zh")
    # # tw.do_translate("baidu", "vi", "zh")
    # print("trans_result:", len(tw.trans_result))

    # tw.rewrite_j()

