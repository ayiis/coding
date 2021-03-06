#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import tornado, tornado.gen, tornado.web
from tornado.options import define, options
import datetime

import config
import do_check

from common import my_logger
logging = my_logger.Logger("schedules.check_available.py", False, True, True)

setting = {
    "running": False,   # when i was running, Lock me
    "db": None,
    "count_remove": 0,
    "count_update": 0,
}


@tornado.gen.coroutine
def do_check_available(proxy_item, ip_data):

    if ip_data:
        setting["count_update"] += 1
        yield setting["db"][config.setting["available_pool"]["db_name"]].update({
            "_id": proxy_item["_id"],
        }, {
            "$set": ip_data
        })

    else:
        setting["count_remove"] += 1

        # move to unavailable_pool
        yield [
            setting["db"][config.setting["available_pool"]["db_name"]].remove({"_id": proxy_item["_id"]}),
            setting["db"][config.setting["unavailable_pool"]["db_name"]].update({
                "proxy_host": proxy_item["proxy_host"],
                "proxy_port": proxy_item["proxy_port"],
            }, { x:proxy_item[x] for x in proxy_item if x != "_id" }, upsert=True, multi=False)
        ]


@tornado.gen.coroutine
def do(db):

    logging.info("Job check_available start!")

    if setting["running"] == True:
        logging.warn("Another Job check_available still running!")

    while setting["running"] == True:
        yield tornado.gen.sleep(1)

    setting["db"] = db

    job_check = do_check.DoCheck({
        "collection": setting["db"][config.setting["available_pool"]["db_name"]],
        "callback_func": do_check_available,
        "page_size":config.setting["available_pool"]["count"] * 2,
        "timeout":config.setting["available_pool"]["timeout"],
    })

    try:
        setting["running"] = True
        yield job_check.do()
    except:
        logging.my_exc("Exception on check_available.")
    finally:
        setting["running"] = False

    logging.info("Job check_available Done!")
    logging.info(setting)
