#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import tornado, tornado.gen, tornado.web
from tornado.options import define, options
import datetime

import config
import do_check

from common import my_logger
logging = my_logger.Logger("schedules.check_unavailable.py", False, True, True)

setting = {
    "db": None,
    "count_remove": 0,
    "count_update": 0,
}

@tornado.gen.coroutine
def do_check_unavailable(proxy_item, ip_data):

    if ip_data:
        setting["count_update"] += 1
        ip_data["data_source"] = proxy_item["data_source"]
        ip_data["create_datetime"] = ip_data["last_validate_datetime"]

        # move to available_pool
        yield [
            setting["db"][config.setting["unavailable_pool"]["db_name"]].remove({"_id": proxy_item["_id"]}),
            setting["db"][config.setting["available_pool"]["db_name"]].update({
                "proxy_host": proxy_item["proxy_host"],
                "proxy_port": proxy_item["proxy_port"],
            }, { x:ip_data[x] for x in ip_data if x != "_id" }, upsert=True, multi=False)
        ]
    else:
        setting["count_remove"] += 1

        # move to fail_pool
        yield [
            setting["db"][config.setting["unavailable_pool"]["db_name"]].remove({"_id": proxy_item["_id"]}),
            setting["db"][config.setting["fail_pool"]["db_name"]].update({
                "proxy_host": proxy_item["proxy_host"],
                "proxy_port": proxy_item["proxy_port"],
            }, { x:proxy_item[x] for x in proxy_item if x != "_id" }, upsert=True, multi=False)
        ]


@tornado.gen.coroutine
def do(db):

    logging.info("Job check_unavailable start!")

    setting["db"] = db

    job_check = do_check.DoCheck({
        "collection": setting["db"][config.setting["unavailable_pool"]["db_name"]],
        "callback_func": do_check_unavailable,
        "page_size":config.setting["unavailable_pool"]["count"] * 2,
        "timeout":config.setting["unavailable_pool"]["timeout"],
    })
    yield job_check.do()

    logging.info("Job check_unavailable Done!")
    logging.info(setting)
