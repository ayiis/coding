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
def do_check_fail(proxy_item, ip_data):

    if ip_data:
        setting["count_update"] += 1
        ip_data["data_source"] = proxy_item["data_source"]
        ip_data["create_datetime"] = ip_data["last_validate_datetime"]

        # move to available_pool
        yield [
            setting["db"][config.setting["fail_pool"]["db_name"]].remove({"_id": proxy_item["_id"]}),
            setting["db"][config.setting["available_pool"]["db_name"]].update({
                "proxy_host": proxy_item["proxy_host"],
                "proxy_port": proxy_item["proxy_port"],
            }, ip_data, upsert=True, multi=False)
        ]
    else:
        setting["count_remove"] += 1

        # remove forever
        yield setting["db"][config.setting["fail_pool"]["db_name"]].remove({"_id": proxy_item["_id"]})


@tornado.gen.coroutine
def do(db):

    print "Job check_fail start!", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    setting["db"] = db

    job_check = do_check.DoCheck({
        "collection": setting["db"][config.setting["fail_pool"]["db_name"]],
        "callback_func": do_check_fail,
        "page_size":config.setting["fail_pool"]["count"] * 2,
        "timeout":config.setting["fail_pool"]["timeout"],
    })
    yield job_check.do()

    print "Job check_fail Done!", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "OUTTER DONE!", setting
