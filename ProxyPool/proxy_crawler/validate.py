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

tmp_db_name = "tmp_validate_db"
validate_site = "https://ayiis.me/ip"

@gen.coroutine
def do(mongodb, db_name, data_source):

    # 以IP为单位，整合到一个临时表里
    mongodb[db_name].aggregate([{
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
        "$out": tmp_db_name
    }])

    # 每次从临时表中取N个IP进行验证
    page_size = config.validate_setting["count"]
    total_size = yield mongodb[tmp_db_name].count()

    total_page = total_size / page_size
    total_page = total_size % page_size == 0 and total_page or total_page + 1
    for page_index in xrange(total_page + 1):
    # for page_index in xrange(1):

        ip_results = yield mongodb[tmp_db_name].find({}, {"_id": 1, "port": 1}).skip(page_index * page_size).limit(page_size).to_list(length=None)

        print "ip_results:", ip_results

        yield_list_id = []
        yield_list = []

        for item in ip_results:
            for port in item["port"]:
                port = int(port)
                print "%s:%s" % (item["_id"], port)
                validate_request = tool.http_request({
                    "url": validate_site,
                    "method": "POST",
                    "headers": {
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
                    },
                    "body": "{\"username\": \"ayiis\"}",
                    "proxy_host": item["_id"],
                    "proxy_port": port,
                    "request_timeout": 30,
                })

                yield_list_id.append( "%s:%s" % (item["_id"], port) )
                yield_list.append(validate_request)

                if len(yield_list) >= page_size:
                    yield analyze_response(yield_list_id, yield_list)
                    yield_list_id, yield_list = [], []

        yield analyze_response(yield_list_id, yield_list)
        yield_list_id, yield_list = [], []


@gen.coroutine
def analyze_response(yield_list_id, yield_list):
    yield_list_result = yield yield_list
    for index, proxy_host in enumerate(yield_list_id):
        response = yield_list_result[index]
        if response.code != 200:
            open("bad_result.json", "a").write("%s\r\n" % (proxy_host))
            continue
        elif response.content not in proxy_host:
            print "200 but. %s not in %s:" % (proxy_host, response.content)
            open("warning_result.json", "a").write("%s in %s\r\n" % (proxy_host, response.content))
            continue
        else:
            print "GOOD!"
            print "%s in %s:", proxy_host, response.content
            open("good_result.json", "a").write("%s in %s\r\n" % (proxy_host, response.content))


@gen.coroutine
def test(mongodb, db_name, data_source):
    try:
        yield do(mongodb, db_name, data_source)
    except Exception as e:
        print traceback.format_exc()

    ioloop.IOLoop.current().stop()
