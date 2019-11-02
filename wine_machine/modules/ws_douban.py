#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2019/08/23
import re
import q
import time
import json
from conf import config
import traceback
import tornado.gen

from common import tool, mongodb
from aytool.spider import pyquery
from modules.fine import douban as fine_douban

from handlers import content_filter

table_rent_a_life = mongodb.DBS["rent_a_life"]


@tornado.gen.coroutine
def update_with_filter(douban_tmp_name):
    """
        1. 用 filter 更新 douban_tmp
        2. 将 douban_tmp 的数据更新到 douban
    """
    yield content_filter.filter_fresh_data(table_rent_a_life[douban_tmp_name], "douban")

    tmp_item_list = yield table_rent_a_life[douban_tmp_name].find({}, {"_id": 0}).to_list(length=None)
    last_update_one = None
    for item in tmp_item_list:
        # del item["_id"]
        last_update_one = table_rent_a_life["douban"].update_one({
            "id": item["id"],
        }, {
            "$set": item
        }, upsert=True)

    if last_update_one:
        yield last_update_one

    print("update count:", len(tmp_item_list))
    # q.d()


@tornado.gen.coroutine
def execute():
    """
        独占式执行:
            1. 先将douban最新数据保存到 douban_tmp
            2. 用 filter 更新 douban_tmp
            3. 将 douban_tmp 的数据更新到 douban
    """
    douban_tmp_name = "douban_tmp"

    douban_config = yield table_rent_a_life["douban_config"].find({"enable": 1}).to_list(length=None)
    date_list = {x["id"]: x["date"] for x in douban_config}
    name_list = {x["id"]: x["group_name"] for x in douban_config}

    douban_group_worker = fine_douban.DoubanGroup(date_list, name_list)

    for group in date_list:

        got_first_date = None
        # 最多翻 99*25 = 2500 条
        for i in range(99):
            result = yield douban_group_worker.get_page(group, i)
            if not result:
                break

            if not got_first_date:
                got_first_date = result[0]

            for item in result:
                """ 下一页可能出现上一页的最后几个结果，所以用 update """
                yield table_rent_a_life[douban_tmp_name].update_one({
                    "id": item["id"],
                }, {
                    "$set": item
                }, upsert=True)

            if douban_group_worker.end_condition(result[-1]):
                print("Reached end_condition:", result[-1])
                break

            yield tornado.gen.sleep(3)

        if got_first_date:
            yield table_rent_a_life["douban_config"].update_one({
                "id": group,
            }, {
                "$set": {
                    "date": got_first_date["date"]
                }
            })

        yield update_with_filter(douban_tmp_name)

        # 清空 douban_tmp 数据
        yield table_rent_a_life[douban_tmp_name].delete_many({})

        yield tornado.gen.sleep(4)


if __name__ == "__main__":
    execute()
