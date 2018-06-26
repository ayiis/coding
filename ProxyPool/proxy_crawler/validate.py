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

from proxy_crawler import (
    validate_www_3322_org as default_validate_site,
    validate_ayiis_me,
)

tmp_collection_name = "tmp_validate_db"
target_collection_name = "available_pool"
request_timeout = 30


@gen.coroutine
def do(mongodb, collection_name, data_source):

    # 以IP为单位，整合到一个临时表里
    yield mongodb[collection_name].aggregate([{
        "$group": {
            "_id": "$proxy_ip",
            "port": {
                "$addToSet": "$proxy_port"
            },
            "create_datetime" : {
                "$first": "$create_datetime",
            },
            "data_source" : {
                "$first": "$data_source",
            },
            "delay" : {
                "$avg": "$delay",
            },
            "count": {
                "$sum": 1
            }
        }
    }, {
        "$out": tmp_collection_name
    }]).to_list(length=None)

    # 每次从临时表中取N个IP进行验证
    page_size = config.validate_setting["count"]
    total_size = yield mongodb[tmp_collection_name].count()

    total_page = total_size / page_size
    total_page = total_size % page_size == 0 and total_page or total_page + 1
    for page_index in xrange(total_page + 1):
        ip_results = yield mongodb[tmp_collection_name].find({}, {"_id": 1, "port": 1}).skip(page_index * page_size).limit(page_size).to_list(length=None)

        print "ip_results:", ip_results

        datetime_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield_list = []
        for item in ip_results:
            for port in item["port"]:
                yield_list.append(
                    default_validate_site.validate(item["_id"], int(port), tool.get_my_ip())
                )

        yield_list = yield yield_list
        for ip_data in yield_list:
            if not ip_data:
                continue

            print "good ip_data:", ip_data

            ip_data.update({
                "data_source": data_source,
                "last_validate_datetime": datetime_now,
                "create_datetime": datetime_now,
            })
            yield save_to_db(mongodb, target_collection_name, ip_data)


@gen.coroutine
def save_to_db(mongodb, collection_name, ip_data):
    insert_result = yield mongodb[collection_name].insert(ip_data)


@gen.coroutine
def do2(mongodb, collection_name, data_source):

    ff = open("reason.txt", "r").read()
    ip_results = [ item.split("in")[0].strip() for item in ff.split("\n") if item.strip() ]

    print "list ip_results:", len(ip_results)
    ip_results = list(set(ip_results))
    print " set ip_results:", len(ip_results)
    ip_results = [ item.split(":") for item in ip_results]

    yield_list = []

    for item in ip_results:
        yield_list.append(
            default_validate_site.validate(item[0], int(item[1]), tool.get_my_ip())
        )

    datetime_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    yield_list = yield yield_list
    for item in yield_list:
        if not item:
            continue

        item.update({
            "data_source": data_source,
            "last_validate_datetime": datetime_now,
            "create_datetime": datetime_now,
        })
        print "item:", item
        yield save_to_db(mongodb, target_collection_name, item)


@gen.coroutine
def test(mongodb, collection_name, data_source):
    try:
        yield do(mongodb, collection_name, data_source)
    except Exception as e:
        print traceback.format_exc()

    ioloop.IOLoop.current().stop()
