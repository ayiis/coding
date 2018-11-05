#!/usr/bin/env python
# encoding:utf8
import sys
import re
import json
import ubelt
import datetime
import traceback

import requests

reload(sys).setdefaultencoding("utf-8")


from_url = """https://www.ximalaya.com/waiyu/18567832/133802552"""
# from_url = """https://www.ximalaya.com/revision/user/pub?page=1&pageSize=10&keyWord=&uid=99076875"""
# target_url = "https://www.ximalaya.com/revision/play/album?albumId=18567832&pageNum=1&sort=1&pageSize=30"


info = {
    "type": None,
    "username": None,
    "albumId": None,
}

global_header = {
    "Connection": """keep-alive""",
    "Pragma": """no-cache""",
    "Cache-Control": """no-cache""",
    "User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36""",
    # "Content-Type": """application/x-www-form-urlencoded;charset=UTF-8""",
    "Accept": """*/*""",
    "Referer": """https://www.ximalaya.com/waiyu/123""",
    # "Accept-Encoding": """gzip, deflate, br""",
    "Accept-Language": """zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7,la;q=0.6,fr;q=0.5""",
    "Cookie": """device_id=xm_1541403284863_jo3zpugvin4aw3; Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070=1541403286; Hm_lpvt_4a7d8ec50cfd6af753c4f8aee3425070=1541403286""",
}


def analyze_url(from_url):

    # """https://www.ximalaya.com/waiyu/18567832/133802552"""
    result = re.match(r"^http[s]?://www\.ximalaya\.com[\/]+([\w]+)[\/]+([\d]+)[\/]+([\d]+)[\/]*", from_url)
    if result:
        info["type"] = "sound"
        info["username"], info["albumId"], _ = result.groups()
        return True

    # """https://www.ximalaya.com/waiyu/18567832/"""
    result = re.match(r"^http[s]?://www\.ximalaya\.com[\/]+([\w]+)[\/]+([\d]+)[\/]*$", from_url)
    if result:
        info["type"] = "sound_list"
        info["username"], info["albumId"] = result.groups()
        return True

    # """https://www.ximalaya.com/waiyu/"""
    result = re.match(r"^http[s]?://www\.ximalaya\.com[\/]+([\w]+)[\/]*$", from_url)
    if result:
        info["type"] = "user"
        info["username"] = result.groups()
        return True

    raise Exception("check your url if it's like: https://www.ximalaya.com/abc123/456/789")


def get_album(albumId, pagenum=1, result_list=None, max_try=5):

    target_url = "https://www.ximalaya.com/revision/play/album?albumId=%s&pageNum=%s&sort=1&pageSize=100" % (albumId, pagenum)
    print "getting:", target_url

    response = requests.get(url=target_url, headers=global_header, data=None)

    if response.status_code == 200:
        response_json = json.loads(response.text)
        result_list = result_list or []
        if response_json.get("data"):
            result_list += response_json["data"].get("tracksAudioPlay") or []
    else:
        print "%s Something Wrong!" % datetime.datetime.now()
        print response
        return []

    if response_json.get("data").get("hasMore") is True and max_try > 0:
        return get_album(albumId, pagenum+1, result_list, max_try-1)
    else:
        return result_list


def download_sound(src, download_path):

    print "gettting:", src

    response = requests.get(url=src, headers=global_header, stream=True, data=None)

    if response.status_code == 200:
        sound_data = response.raw.read()

        if len(sound_data) < 1:
            raise Exception("No data")
        else:
            open(download_path, "wb").write(sound_data)
    else:
        print "%s Something Wrong!" % datetime.datetime.now()
        print response


def main():
    albumId_list = []
    analyze_url(from_url)
    if info.get("albumId"):
        result_list = get_album(info["albumId"])
        # result_list = json.loads(open("zz.txt", "r").read())
        print info["albumId"], " have result_list count:", len(result_list)
    else:
        pass
        # get user's albumIds
        # for albumId in albumIds:
        #    get_album(info["albumId"])

    for item in result_list:
        print "%s + %-36s %s" % (item["albumName"], item["trackName"], item["src"])
        download_dir = "download/%s/%s" % (item["anchorId"], item["albumName"])
        ubelt.ensuredir(download_dir)
        download_path = "%s/%s.%s" % (download_dir, item["trackName"], item["src"].split(".")[-1] or "m4a")
        try:
            download_sound(item["src"], download_path)
        except Exception:
            print traceback.format_exc()
            pass
            raise


if __name__ == "__main__":
    main()
