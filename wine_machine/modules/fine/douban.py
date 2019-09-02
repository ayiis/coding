#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2019/08/23
import re
import q
import time
import requests
import json
from conf import config
import traceback
import tornado.gen

from common import tool, mongodb
from aytool.spider import pyquery

"""
    爬虫由三个问题构成：

    1. 从哪里开始
    2. 要获取什么内容
    3. 什么时候结束
"""

"""
要处理一种情况：爬行中途出问题了，如何接着处理
    ok, 更新[最后回应]的操作（保存进度）放在爬完小组之后，如果中途出问题，下次任务还是以上次进度算
"""

WEBSITE = "https://www.douban.com"
PAGE_STRUCT = "https://www.douban.com/group/%s/discussion?start=%s"


class DoubanGroup(object):

    def __init__(self, date_list, name_list):
        super(DoubanGroup, self).__init__()
        self.date_list = date_list
        self.name_list = name_list

    def end_condition(self, item):
        """
            [最后回应] < date (上次刷新到的最新的[最后回应])
        """
        return self.date_list[item["group"]] > item["date"]

    def get_price_from_item(self, item):
        """
            从标题匹配 3位到4位 数字 ，视为价格
        """
        price_list = re.findall(r"(\d+)", item["title"])
        if price_list:
            price = next((p for p in price_list if 2 < len(p) < 5), "0")
            return int(price)

        return 0

    @tornado.gen.coroutine
    def get_page(self, group, i):
        """
            []
        """
        page_url = PAGE_STRUCT % (group, i * 25)
        tool.aprint("doing:", page_url)

        res = yield tool.http_request({
            "url": page_url,
            "method": "GET",
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
                "Referer": page_url,
                "Pragma": "no-cache",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            }
        })
        open("www.douban.com.html", "wb").write(res.body)
        content = open("www.douban.com.html", "r").read()

        # news_list
        content_dom = pyquery.parse_content_to_dom(content)
        content_ele = content_dom.find("#content").find("table>tr:gt(0)")

        result_list = []
        for i, content in pyquery.iter_eles(content_ele):
            title = content.find("td").eq(0).find("a").attr("title")
            href = content.find("td").eq(0).find("a").attr("href")

            author = content.find("td").eq(1).find("a").text()
            author_href = content.find("td").eq(1).find("a").attr("href")

            comment = content.find("td").eq(2).text()
            date = content.find("td").eq(3).text()

            result_list.append({
                "group": group,
                "group_name": self.name_list[group],
                "title": title,
                "href": href,
                "author": author,
                "comment": comment or "0",
            })
            # date: 2014-05-31 || 08-23 15:29
            if ":" in date:
                date = "%s-%s:00" % (tool.get_date_string()[:4], date)
            else:
                date = "%s 00:00:00" % (date)
            result_list[-1]["date"] = date
            result_list[-1]["id"] = int(href.split("/")[-2])
            result_list[-1]["author_id"] = author_href.split("/")[-2]
            result_list[-1]["price"] = self.get_price_from_item(result_list[-1])

        tool.aprint("result:", len(result_list))
        return result_list
