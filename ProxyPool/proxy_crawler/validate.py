#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import datetime, time
import re
import traceback
import json
import config

import tornado
from tornado import gen, ioloop, httpclient
from urllib import urlencode
from common import tool, tornado_timmer

from common import (
    tool,
    tornado_pool,
)

from proxy_crawler import (
    validate_www_3322_org as default_validate_site,
    validate_ayiis_me,
)

target_collection_name = "available_pool"


class DoValidate(object):

    def __init__(self, arg):
        super(DoValidate, self).__init__()
        self.setting = {
            "stop": False,
            "total": 0,
            "done": 0,
            "good": 0,

            "callback_func": arg["callback_func"],
            "timeout": arg["timeout"],

            "collection": arg["collection"],
            "ObjectId": None,
            "page_size": arg["page_size"],
            "my_ip": tool.get_my_ip(),

            "data_list": [],
            "generate_next_hold": False,
        }


    def get_next_data(self):

        if self.setting["ObjectId"]:
            find_req = {
                "_id": {
                    "$gt": self.setting["ObjectId"]
                }
            }
        else:
            find_req = {}

        return self.setting["collection"].find(find_req, {
            "_id" : 1,
            "proxy_host" : 1,
            "proxy_port" : 1,
        }).sort([("_id", 1)]).limit(self.setting["page_size"]).to_list(length=None)


    @tornado.gen.coroutine
    def generate_next(self, pool):

        while self.setting["generate_next_hold"]: yield tornado.gen.sleep(0.1)

        if not self.setting["data_list"] and not self.setting["stop"]:

            self.setting["generate_next_hold"] = True
            self.setting["data_list"] = yield self.get_next_data()
            self.setting["generate_next_hold"] = False

            if self.setting["data_list"]:
                self.setting["total"] += len(self.setting["data_list"])
                self.setting["ObjectId"] = self.setting["data_list"][-1]["_id"]
            else:
                # shall be stop
                self.setting["stop"] = True

        if not self.setting["stop"]:
            raise tornado.gen.Return(self.setting["data_list"].pop())
        else:
            # will be call many times
            pool.stop()
            raise tornado.gen.Return(None)


    @tornado.gen.coroutine
    def fork(self, pool):

        proxy_item = yield self.generate_next(pool)

        if proxy_item:

            yield self.validate(proxy_item)

            self.setting["done"] = self.setting["done"] + 1

            # print {x:self.setting[x] for x in self.setting if x not in ("data_list", "collection") }

        # exit pool
        if self.setting["stop"] and self.setting["done"] == self.setting["total"]:
            pool.exit()


    @tornado.gen.coroutine
    def validate(self, proxy_item):

        ip_data = yield default_validate_site.validate(
            proxy_item["proxy_host"],
            int(proxy_item["proxy_port"]),
            self.setting["my_ip"],
            self.setting["timeout"]
        )

        try:
            yield self.setting["callback_func"](proxy_item, ip_data)
        except Exception, e:
            print traceback.format_exc()


    @tornado.gen.coroutine
    def do(self):

        pool = tornado_pool.WorkerPool({
            "func": self.fork,
            "pool_size": self.setting["page_size"],
        })

        yield pool.start_pool()

        # DONE - print for debug
        print { x:self.setting[x] for x in self.setting if x not in ("data_list", "collection", "generate_next_hold") }


@gen.coroutine
def do(mongodb, collection_name, data_source):

    print "Job validate for %s (%s) start at %s!" % (collection_name, data_source, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @tornado.gen.coroutine
    def do_validate(proxy_item, ip_data):

        if ip_data:
            ip_data["data_source"] = data_source
            ip_data["create_datetime"] = ip_data["last_validate_datetime"]

            # just for infomation
            job_check.setting["good"] += 1

            # move to available_pool
            yield mongodb[target_collection_name].update({
                "proxy_host": proxy_item["proxy_host"],
                "proxy_port": proxy_item["proxy_port"],
            }, { x:ip_data[x] for x in ip_data if x != "_id" }, upsert=True, multi=False)
        else:
            # do nothing
            pass

    tmp_collection_name = "tmp_%s_%s" % (collection_name, int(time.time()))

    # 去重, 整合到一个临时表里
    yield mongodb[collection_name].aggregate([{
        "$group": {
            "_id": {
                "proxy_host": "$proxy_host",
                "proxy_port": "$proxy_port",
            },
        }
    }, {
        "$project": {
            "_id": 0,
            "proxy_host": "$_id.proxy_host",
            "proxy_port": "$_id.proxy_port",
        }
    }, {
        "$out": tmp_collection_name
    }]).to_list(length=None)

    job_check = DoValidate({
        "collection": mongodb[tmp_collection_name],
        "callback_func": do_validate,
        "page_size": config.validate_setting["count"],
        "timeout": config.validate_setting["timeout"],
    })
    yield job_check.do()

    # drop tmp collection
    yield mongodb[tmp_collection_name].drop()

    print "Job validate for %s (%s) Done at %s!" % (collection_name, data_source, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print "OUTTER DONE!", job_check.setting
