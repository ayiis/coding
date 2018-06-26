#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import tornado, tornado.gen, tornado.web
from tornado.options import define, options
import datetime

import config
import do_check

setting = {
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
            setting["db"][config.setting["unavailable_pool"]["db_name"]].insert(proxy_item),
        ]


@tornado.gen.coroutine
def do(db):

    setting["db"] = db

    job_check = do_check.DoCheck({
        "db": setting["db"][config.setting["available_pool"]["db_name"]],
        "callback_func": do_check_available,
        "page_size":config.setting["available_pool"]["count"] * 2,
        "timeout":config.setting["available_pool"]["timeout"],
    })
    yield job_check.do()

    print "Job check_available Done!", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "OUTTER DONE!", setting
