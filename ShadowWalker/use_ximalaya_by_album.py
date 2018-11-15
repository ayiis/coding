#!/usr/bin/env python
# encoding:utf8
import sys
import re
import json
import ubelt
from pathlib import Path
import traceback
from ubelt.util_io import exists
import requests
import my_json

reload(sys).setdefaultencoding("utf-8")

keyword_list = [
    r"raz aa",
    r"raz a",
    r"raz b",
    r"raz c",
    r"raz d",
    r"raz e",
    r"raz f",
    r"raz g",
    r"raz h",
    r"raz i",
    r"raz j",
    r"raz k",

    r"razaa",
    r"raza",
    r"razb",
    r"razc",
    r"razd",
    r"raze",
    r"razf",
    r"razg",
    r"razh",
    r"razi",
    r"razj",
    r"razk",
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

TARGET_DIR = "/data/1113/"


def get_album(albumId, pagenum=1, result_list=None, max_try=2):

    target_url = "https://www.ximalaya.com/revision/play/album?albumId=%s&pageNum=%s&sort=1&pageSize=100" % (albumId, pagenum)
    print "getting:", target_url

    response = requests.get(url=target_url, headers=global_header, data=None)

    if response.status_code == 200:
        response_json = json.loads(response.text)
        result_list = result_list or []
        if response_json.get("data"):
            result_list += response_json["data"].get("tracksAudioPlay") or []
    else:
        print response
        return []

    if response_json.get("data").get("hasMore") is True and max_try > 0:
        return get_album(albumId, pagenum+1, result_list, max_try-1)
    else:
        return result_list


def download_sound(src, download_path, max_try=2):

    # print "gettting:", src

    response = requests.get(url=src, headers=global_header, stream=True, data=None)

    if response.status_code == 200:
        sound_data = response.raw.read()

        if len(sound_data) < 1:
            raise Exception("No data")
        else:
            open(download_path, "wb").write(sound_data)
    else:
        print response
        download_sound(src, download_path, max_try-1)


def filter_ad(item):
    ad_word = ur"老师|出品|讲解|启蒙|微信|提供|水平|原音|淘宝|著名|http|公号|关注|资料|资源|更多|电子书|pdf|公益|读物|频道|外教|经验|美国|法语|每日|计划|录音室|工作室"
    if re.search(ad_word, "%s %s %s" % (item["title"], item["intro"], item["richTitle"]), re.DOTALL | re.M):
        return False

    ad_word_end = ur"网$|阅读$|英语$|教育$|老师$|室$"
    if re.search(ad_word_end, item["nickname"], re.DOTALL | re.M):
        return False

    if re.search(ad_word_end, item["title"], re.DOTALL | re.M):
        return False

    if re.search(ad_word_end, item["intro"], re.DOTALL | re.M):
        return False

    if re.search(ad_word_end, item["richTitle"], re.DOTALL | re.M):
        return False

    return True


def get_albumId_list(keyword, pagenum=1, result_list=None, max_try=20):
    album_list_url = c_album_list_url % (keyword, pagenum, 100)
    print "album_list_url:", album_list_url

    response = requests.get(url=album_list_url, headers=global_header, data=None)

    if response.status_code == 200:
        # print "len:", response.text
        response_json = json.loads(response.text)
        result_list = result_list or []
        if response_json.get("data") and response_json.get("ret") == 200:
            result_list += list(filter(lambda x: filter_ad(x), response_json["data"]["result"]["response"]["docs"]))
        else:
            print "msg:", response_json.get("msg")
            return result_list or []
    else:
        print response
        return result_list or []

    if pagenum < response_json["data"]["result"]["response"]["totalPage"] and max_try > 0:
        return get_albumId_list(keyword, pagenum+1, result_list, max_try-1)
    else:
        return result_list


def format_track_name(track_name):
    track_name = track_name.lower()
    track_name = re.sub(r"[^a-z]", " ", track_name)
    track_name = re.sub(r"[ ]{2,}", " ", track_name)
    track_name = track_name.strip().replace(" ", "_")
    track_name = "_%s_" % track_name
    return track_name


def cache_all_track_name():

    for path in Path("catalog").glob("*"):
        level = path.name.split("_")[-1]
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


def do_grep_keyword_result():

    for keyword in keyword_list:

        try:
            print "working on keyword:%s" % keyword
            albumId_list = get_albumId_list(keyword)

            if not albumId_list:
                print "nothing is in %s" % keyword
                continue

        except Exception:
            print traceback.format_exc()
            continue

        with open("procing_1/%s.log" % keyword, "w") as fw:
            fw.write(my_json.json_stringify(albumId_list))

        # break


def do_grep_album():

    for keyword in keyword_list:

        keyname = keyword.replace("raz", "").replace(" ", "")

        try:
            albumId_list = my_json.json_load(open("procing_1/%s.log" % keyword, "r").read())
        except Exception:
            print traceback.format_exc()
            continue

        print "procing: %s * %s * %s" % (keyname, keyword, len(albumId_list))

        procing_2_cache = {}
        for item in albumId_list:
            albumId = item["id"]
            result_list = get_album(albumId)

            print "album %s length is: %s" % (item["title"], len(result_list))

            for item in result_list:

                if not item["trackName"] or not item["src"]:
                    print "Error no name: %s", item
                    continue

                fixed_name = check_track_name(item["trackName"], keyname)
                if not fixed_name:
                    print "not found in [%s] * [%s] * [%s]" % (keyname, format_track_name(item["trackName"]), item["trackName"])
                    continue

                cache_key = "%s%s___%s" % (albumId, keyname, fixed_name)
                procing_2_cache[cache_key] = item["src"]

            # break

        with open("procing_2/%s.log" % keyword, "w") as fw:
            fw.write(my_json.json_stringify(procing_2_cache))

        # break


def download_all_sound():

    for keyword in keyword_list:

        try:
            download_list = my_json.json_load(open("procing_2/%s.log" % keyword, "r").read())
        except Exception:
            print traceback.format_exc()
            continue

        print "downloading: %s" % len(download_list)

        for i, key in enumerate(download_list):
            target_dir = "%s%s" % (TARGET_DIR, key)
            ubelt.ensuredir(target_dir)
            target_path = target_dir + "/raw.m4a"

            if not download_list[key]:
                print "key %s is empty." % key
                continue

            if exists(target_path):
                print "exists: %s" % target_path
            else:
                print "[%s] [%3s/%3s] %s" % (keyword, i, len(download_list), key)
                download_sound(download_list[key], target_path)

        #     break

        # break


def main():

    cache_all_track_name()

    do_grep_keyword_result()

    do_grep_album()

    download_all_sound()


if __name__ == "__main__":
    main()
