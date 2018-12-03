#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import traceback
import time
import requests
from lxml import etree
from pyquery import PyQuery as pq
import sys
import ubelt
from ubelt.util_io import exists
import my_json
import zlib


reload(sys).setdefaultencoding("utf8")


key_words = [
    # "shafachajizuhe",   # "沙发茶几组合",
    "canzhuozuhe",  # "餐桌组合",
    "canguizuhe",   # "餐柜组合",
    "geduanguizuhe",    # "隔断柜组合",
    "xieguizuhe",   # "鞋柜组合",
    "bataizuhe",    # "吧台组合",
    "zhuangshiguizuhe", # "装饰柜组合",
    "ttm_kcanting-96",  # "榻榻米与书柜组合",
    "ttm_kcanting-97",  # "榻榻米与书桌组合",
    "ttm_kcanting-98",  # "榻榻米与飘窗组合",
    "ttm_kcanting-99",  # "其他组合",
    "ttm_kcanting", # "榻榻米客餐厅组合",
    "yimaojian-7",  # "L型",
    "yimaojian-8",  # "U型",
    "yimaojian",    # "衣帽间",
    "chuang-20",    # "床与床头柜组合",
    "chuang-21",    # "床与梳妆台组合",
    "chuang-22",    # "床与书桌组合",
    "chuang-31",    # "床与装饰柜组合",
    "chuang-33",    # "其它",
    "chuang",   # "床组合",
    "dianshigui-23",    # "电视柜与梳妆台组合",
    "dianshigui-24",    # "电视柜与书桌组合",
    "dianshigui-25",    # "电视柜与装饰柜",
    "dianshigui-30",    # "其它",
    "dianshigui",   # "电视柜组合",
    "woshizhuangshigui-32", # "装饰柜与梳妆台",
    "woshizhuangshigui-34", # "装饰柜与书桌",
    "woshizhuangshigui-76", # "装饰柜组合",
    "woshizhuangshigui",    # "装饰柜组合",
    "piaochuang-39",    # "飘窗与梳妆台组合",
    "piaochuang-27",    # "飘窗与书台组合",
    "piaochuang-28",    # "飘窗与电视柜组合",
    "piaochuang-29",    # "飘窗与书柜组合",
    "piaochuang-38",    # "其它",
    "piaochuang",   # "飘窗利用",
    "ttm_wofang-84",    # "榻榻米与书柜组合",
    "ttm_wofang-85",    # "榻榻米与书桌组合",
    "ttm_wofang-86",    # "榻榻米与飘窗组合",
    "ttm_wofang-87",    # "其他组合",
    "ttm_wofang",   # "榻榻米卧房组合",
    "shuzhuo",  # "直角书桌组合",
    "zhuanjiaoshuzhuo", # "转角书桌组合",
    "shufanggui",   # "多功能室组合",
    "tatami",   # "榻榻米",
    "shufangjiaju", # "其他",
    "ertongchuang", # "上下床",
    "ertongshugui", # "书柜组合",
    "ertongshuzhuo",    # "书桌组合",
    "ertongpiaochuang", # "飘窗利用",
    "ertongtatami", # "榻榻米",
    "ttm_qshaonian-92", # "榻榻米与书柜组合",
    "ttm_qshaonian-93", # "榻榻米与书桌组合",
    "ttm_qshaonian-94", # "榻榻米与飘窗组合",
    "ttm_qshaonian-95", # "其他组合",
    "ttm_qshaonian",    # "榻榻米青少年房组合",
    "ertongjiaju",  # "其它",
    "ttm_yigui",    # "榻榻米衣柜组合",
    # "shafa",    # "沙发茶几组合",
    "geduangui",    # "隔断柜组合",
    "xiegui",   # "鞋柜组合",
    "batai",    # "吧台组合",
    "zhuangshigui", # "装饰柜组合",
    "cangui",   # "餐柜组合",
    "cantingxiegui",    # "鞋柜组合",
    "L-chugui", # "L型",
    "U-chugui", # "U型"
]

c_c_list_url = """http://www.homekoo.com/%s-p%s-fen_num_desc"""


global_header = {
    "Connection": """closed""",
    "Accept": """*/*""",
    # "Accept-Encoding": """gzip, deflate""",
    "Accept-Language": """zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7,la;q=0.6,fr;q=0.5,hmn;q=0.4""",
    "Cookie": """acw_tc=76b20fe415436448055396048e3d32f84a400826d3bbf2007b99066b23176d; _homekoo_city_quhao=020; my_visit_date=2018-12-01; my_visit_num=1; my_visit_ip=59.42.106.170; open_window=1543644831; openpnum=1; tq_current_visit_time=1543644834551; db_=3toSsOwnKqnGct%2Bh8MfNpPoDEdSK8TBV81T4i5uh%2BCnm2A; others=3owX6r8oe6%2FEcN6Q1DIwgHPRrk2z9TFW9lT7ipqevn29hLaPpyrc; UM_distinctid=1676867020e6ee-0257d5f723d49f-5b183a13-1fa400-1676867020f529; CNZZDATA5893770=cnzz_eid%3D996572898-1543639652-%26ntime%3D1543639652""",
    # "Referer": """http://www.homekoo.com/shafa-p2-fen_num_desc""",
    "User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36""",
}


def gzip_decode(g_data):
    return zlib.decompress(g_data, zlib.MAX_WBITS | 32)


def grep_end_page(pquery):
    try:
        last_end = pquery.find("#big_image_list").find(".no3").text()
        return int(last_end)
    except Exception:
        return 0


def get_content(url, max_try=2):
    print "url:", url
    try:
        response = requests.get(url=url, headers=global_header, data=None, timeout=5)
    except Exception:
        print traceback.format_exc()
        if max_try > 0:
            return get_content(url, max_try-1)
        else:
            return None

    if response.status_code == 200:
        return response.text

    elif max_try > 0:
        return get_content(url, max_try-1)


def analyze(pquery):
    result_list = []
    dt_list = pquery.find("#big_image_list").find(".tu_list").find("dt").filter(lambda i, this: not pq(this).find(".bbs_bm_img"))
    for item in dt_list:
        item = pq(item)
        try:
            res = {
                "src": item.find(".later").attr("data-original") or "",
                "alt": item.find(".later").attr("title") or None,
                "tag": item.find("h3 a").attr("title") or None,
                "title": item.find("h3 a").text() or None,
                "price": int(item.find(".tj").text().replace("￥", "")) or None,
            }
            if res["src"][:2] == "//":
                res["src"] = "http:" + res["src"]
            if res["src"][-12:] == ".300_225.jpg":
                res["src"] = res["src"].replace(".300_225.jpg", "")

        except Exception:
            print traceback.format_exc()

        result_list.append(my_json.json_stringify(res))

    return result_list


def save_to_db(keyword, result_list):
    with open("/data/homekoo/homekoo_%s_result.log" % keyword, "a") as af:
        af.write("\r\n".join(result_list))
        af.write("\r\n")


def get_image(src, download_path, max_try=2):

    print "gettting:", src

    try:
        response = requests.get(url=src, headers=global_header, stream=True, data=None, timeout=5)
    except Exception:
        print traceback.format_exc()
        if max_try > 0:
            return get_image(src, download_path, max_try-1)
        else:
            return None

    if response.status_code == 200:
        sound_data = response.raw.read()

        if sound_data[:4] == "\x1f\x8b\x08\x00":
            sound_data = gzip_decode(sound_data)

        # print "sound_data:", sound_data[:4].encode("hex")

        if len(sound_data) < 1:
            raise Exception("No data")
        else:
            open(download_path, "wb").write(sound_data)
    elif max_try > 0:
        print response
        get_image(src, download_path, max_try-1)


def download_images(keyword):
    with open("/data/homekoo/homekoo_%s_result.log" % keyword, "r") as rf:
        data_list = list(rf.readlines())
        total = len(data_list)
        print "total lines is:", total
        ubelt.ensuredir("/data/homekoo/%s" % keyword)
        for i, item in enumerate(data_list):

            if i % 10 == 9:
                print "downloading: %s/%s" % (i, total)

            item = my_json.json_load(item)
            if not item["src"]:
                continue

            download_path = "/data/homekoo/%s/%s" % (keyword, item["src"].split("/")[-1])
            if exists(download_path):
                print "exists: %s" % download_path
                continue

            try:
                get_image(item["src"], download_path)
            except Exception:
                print traceback.format_exc()


def main():

    for keyword in key_words:

        print "working on [%s]" % (keyword)

        print "start download images of [%s]" % (keyword)
        try:
            download_images(keyword)
        except Exception:
            print traceback.format_exc()

        continue

        try:
            start_page_html = get_content(c_c_list_url % (keyword, 1))
            start_page_html = pq(start_page_html)
            end_page = grep_end_page(start_page_html)
        except Exception:
            end_page = 0

        print "end_page of [%s] is : %s" % (keyword, end_page)

        for page_i in range(1, end_page+1):

            try:
                page_html = get_content(c_c_list_url % (keyword, page_i))
                page_html = pq(page_html)
                result_list = analyze(page_html)
                save_to_db(keyword, result_list)
            except Exception:
                print traceback.format_exc()

            print "page %s/%s of [%s] done!" % (page_i, end_page, keyword)

            # exit(1)

            # time.sleep(1)

        # print "start download images of [%s]" % (keyword)
        # download_images(keyword)


if __name__ == "__main__":
    main()
