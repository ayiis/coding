#!/usr/bin/env python
# encoding:utf8
import sys
import re
import shutil
import json
import ubelt
from pathlib import Path
import traceback
from ubelt.util_io import exists
import requests
import my_json

reload(sys).setdefaultencoding("utf-8")

keyword_list = [
    r"aa",
    r"a",
    r"b",
    r"c",
    r"d",
    r"e",
    r"f",
    r"g",
    r"h",
    r"i",
    r"j",
    r"k",
]


c_album_list_url = """https://www.ximalaya.com/revision/search?core=album&kw=%s&page=%s&spellchecker=false&rows=%s&condition=relation&device=iPhone&fq=&paidFilter=true"""
c_sound_list_url = """https://www.ximalaya.com/revision/play/album?albumId=%s&pageNum=%s&sort=1&pageSize=30"""

global_header = {
    "Connection": """closed""",
    "Pragma": """no-cache""",
    "Cache-Control": """no-cache""",
    "User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36""",
    "Accept": """*/*""",
    "Referer": """https://www.ximalaya.com/waiyu/123""",
    # "Accept-Encoding": """gzip, deflate, br""",
    "Accept-Language": """zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7,la;q=0.6,fr;q=0.5""",
    "Cookie": """device_id=xm_1541403284863_jo3zpugvin4aw3; Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070=1541403286; Hm_lpvt_4a7d8ec50cfd6af753c4f8aee3425070=1541403286""",
}

track_name_list = {
    "aa": set([]),
    "a": set([]),
    "b": set([]),
    "c": set([]),
    "d": set([]),
    "e": set([]),
    "f": set([]),
    "g": set([]),
    "h": set([]),
    "i": set([]),
    "j": set([]),
    "k": set([]),
}

SOURCE_DIR = "/wav_data/1113_done/"
DONE_DIR = "/home/1109_done/"
TARGET_DIR = "/wav_data/1113_out_list/"
DONE_TARGET_DIR = "/wav_data/1113_out_1109/"


def format_track_name(track_name):
    track_name = track_name.lower()
    track_name = re.sub(r"[^a-z]", " ", track_name)
    track_name = re.sub(r"[ ]{2,}", " ", track_name)
    track_name = track_name.strip().replace(" ", "_")
    track_name = "_%s_" % track_name
    return track_name


def cache_all_track_name():

    for path in Path("title_new").glob("*"):
        level = path.name.split("_")[0].lower()
        path = "%s" % path
        with open(path, "r") as fr:
            for track_name in fr.readlines():
                track_name = format_track_name(track_name)
                if track_name:
                    track_name_list[level].add(track_name)


def check_track_name(track_name, level):

    track_name = format_track_name(track_name)

    for known_name in track_name_list[level]:
        if known_name in track_name:
            return known_name[1:-1]

    return None


def do_match_none():
    for path in Path(SOURCE_DIR).glob("*___*"):
        level = re.sub(r"[0-9]+", "", path.name.split("___")[0])
        f_name = path.name.split("___")[1].replace("_", " ").strip()
        f_name = "_%s_" % f_name.replace(" ", "_")

        for known_name in track_name_list[level]:
            if known_name == f_name:
                break
        else:
            print "[ %s ] is not in the list of [ %s ]" % (f_name, level)
            shutil.move("%s" % path, "%s%s" % (TARGET_DIR, path.name))


def do_match_done():
    for path in Path(DONE_DIR).glob("*___*"):
        album_name = path.name.split("___")[0]
        print "album_name:", album_name

        for path2 in Path(SOURCE_DIR).glob("%s___*" % album_name):
            print "path2:", "%s" % path2
            print "target:", "%s%s" % (DONE_TARGET_DIR, path2.name)

            shutil.move("%s" % path2, "%s%s" % (DONE_TARGET_DIR, path2.name))


def main():

    cache_all_track_name()

    do_match_none()

    do_match_done()


if __name__ == "__main__":
    main()
