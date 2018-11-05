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


userid = "85488140"

c_album_list_url = """https://www.ximalaya.com/revision/user/pub?page=%s&pageSize=10&keyWord=&uid=%s"""
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


def get_album(albumId, pagenum=1, result_list=None, max_try=2):

    target_url = "https://www.ximalaya.com/revision/play/album?albumId=%s&pageNum=%s&sort=1&pageSize=100" % (albumId, pagenum)
    # print "getting:", target_url

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


def get_albumId_list(userid, pagenum=1, result_list=None, max_try=2):
    album_list_url = c_album_list_url % (pagenum, userid)
    # print "album_list_url:", album_list_url

    response = requests.get(url=album_list_url, headers=global_header, data=None)

    if response.status_code == 200:
        response_json = json.loads(response.text)
        result_list = result_list or []
        if response_json.get("data"):
            result_list += response_json["data"].get("albumList") or []
    else:
        print response
        return []

    if response_json.get("data").get("hasMore") is True and max_try > 0:
        return get_albumId_list(userid, pagenum+1, result_list, max_try-1)
    else:
        return result_list


def main():
    albumId_list = get_albumId_list(userid)
    if not albumId_list:
        print "nothing is in %s" % userid
        return

    info = {
        "anchorNickName": albumId_list[0]["anchorNickName"],
        "anchorUid": albumId_list[0]["anchorUid"],
    }

    print "album length is: %s" % len(albumId_list)

    for item in albumId_list:
        albumId = item["id"]
        result_list = get_album(albumId)

        print "album %s length is: %s" % (item["title"], len(result_list))

        for item in result_list:
            print "%s + %-36s %s" % (item["albumName"], item["trackName"], item["src"])
            download_dir = "download/%s - %s/%s - %s" % (info["anchorUid"], info["anchorNickName"], albumId, item["albumName"])
            ubelt.ensuredir(download_dir)
            download_path = "%s/%s.%s" % (download_dir, item["trackName"], item["src"].split(".")[-1] or "m4a")
            try:
                download_sound(item["src"], download_path)
            except Exception:
                print traceback.format_exc()
                raise

        #     break
        # break


if __name__ == "__main__":
    main()
