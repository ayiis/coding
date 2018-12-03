#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    用于没有返回总页数的搜索页
    MAX_TRY=999
"""
import re
import traceback
import time
import requests
from pyquery import PyQuery as pq
import sys
import ubelt
from ubelt.util_io import exists
import zlib
import my_json

MAX_TRY = 999
KEYWORD = "尚品宅配"

reload(sys).setdefaultencoding("utf8")

c_c_search_url = """http://so.mama.cn/search"""
c_search_url = """http://so.mama.cn/search?source=all&q=尚品宅配&csite=all&size=50&sortMode=1&page=1"""

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


def get_search_result(url, max_try=2):
    print "url:", url

    try:
        response = requests.get(url=url, headers=global_header, data=None, timeout=5)
    except Exception:
        print traceback.format_exc()
        if max_try > 0:
            return get_search_result(url, max_try-1)
        else:
            return None

    if response.status_code == 200:
        return response.text

    elif max_try > 0:
        return get_search_result(url, max_try-1)


def analyze(pquery):
    result_list = []
    alist = pquery.find(".main>div")
    for item in alist:
        item = pq(item)
        try:

            if KEYWORD not in item.text():
                continue
            href = item.find("h1>a").attr("href")
            if href:
                result_list.append(href)

        except Exception:
            print traceback.format_exc()

    if pquery.find(".pagination>a:last").text() == "下一页":
        next_page = "%s%s" % (c_c_search_url, pquery.find(".pagination>a:last").attr("href"))
    else:
        next_page = None

    return next_page, result_list


def save_to_db(result_list):
    with open("/data/homekoo/text_homekoo_mamacn_result.log", "a") as af:
        af.write("\r\n".join(result_list))
        af.write("\r\n")


def handle_content(content, download_path):
    try:

        pquery = pq(content)
        res = []
        res.append(pquery.find("#fjump").parent().text())
        postlist = pquery.find("#postlist>div").find(".t_f")
        for tf in postlist:
            try:
                pq(tf).find(".pstatus").remove()
                pq(tf).find(".quote").remove()
                pq(tf).find("strong").remove()
                text = pq(tf).text()
                text = "\r\n".join([x for x in text.replace("\r", "\n").split("\n") if x and "该信息来自" not in x])

                res.append(text)
            except Exception:
                print traceback.format_exc()

        if res:
            with open(download_path, "a") as af:
                af.write(("\r\n============\r\n").join(res))
                af.write("\r\n============\r\n")

        if pquery.find("#pgt .pg>a:last").text() == "下一页":
            return pquery.find("#pgt .pg>a:last").attr("href")

    except Exception:
        print traceback.format_exc()

    return None


def get_content(target_url, download_path, max_try=2):

    print "gettting:", target_url

    try:
        response = requests.get(url=target_url, headers=global_header, data=None, timeout=5)
    except Exception:
        print traceback.format_exc()
        if max_try > 0:
            return get_content(target_url, download_path, max_try-1)
        else:
            return None

    if response.status_code == 200:
        content = response.text

        if len(content) < 1:
            raise Exception("No data")
        else:
            return handle_content(content, download_path)

    elif max_try > 0:
        print response
        return get_content(target_url, download_path, max_try-1)


def get_all_content(target_url, download_path):

    next_page = target_url
    for i in xrange(MAX_TRY):

        try:
            next_page = get_content(next_page, download_path)
            print "|next page:", next_page
        except Exception:
            print traceback.format_exc()

        if not next_page:
            print "seems done! total is %s page" % (i + 1)
            break
    else:
        print "get_all_content OVER STACK of MAX_TRY"


def download_content():
    with open("/data/homekoo/text_homekoo_mamacn_result.log", "r") as rf:
        data_list = list(rf.readlines())
        total = len(data_list)
        print "total lines is:", total
        ubelt.ensuredir("/data/homekoo/text_mamacn")
        for i, target_url in enumerate(data_list):

            if i % 10 == 9:
                print "crawling: %s/%s" % (i, total)

            # todo
            # do one thing one time
            if re.match("http://www.gzmama.com/", target_url, re.I):

                tid = 0
                if re.match(r"http://www.gzmama.com/thread-(\d+)-\d+-\d+.html", target_url, re.I):
                    tid = re.match(r"http://www.gzmama.com/thread-(\d+)-\d+-\d+.html", target_url, re.I).groups()[0]
                elif re.match(r"http://www.gzmama.com/forum.php\?.*&tid=(\d+)", target_url, re.I):
                    tid = re.match(r"http://www.gzmama.com/forum.php\?.*&tid=(\d+)", target_url, re.I).groups()[0]
                else:
                    print "cannot get tid of %s" % target_url
                    continue

                print "target_url: %s - %s" % (tid, target_url)

                download_path = "/data/homekoo/text_mamacn/%s.html" % (tid)
                if exists(download_path):
                    print "exists: %s" % download_path
                    continue

                try:
                    get_all_content(target_url, download_path)
                except Exception:
                    print traceback.format_exc()


def main():

    next_page = c_search_url

    download_content()
    exit(1)

    for i in xrange(MAX_TRY):

        try:
            page_html = get_search_result(next_page)
            page_html = pq(page_html)
            next_page, result_list = analyze(page_html)
            # print result_list
            print "|next page:", next_page
            save_to_db(result_list)
        except Exception:
            print traceback.format_exc()
            break

        if not next_page:
            print "seems done! total is %s page" % (i + 1)
            break

    else:
        print "main OVER STACK of MAX_TRY"


if __name__ == "__main__":
    main()
