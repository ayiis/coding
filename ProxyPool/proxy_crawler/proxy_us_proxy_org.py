#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import datetime, time
import re
import traceback
import json
from lxml import etree

import tornado
from tornado import gen, ioloop, httpclient
from urllib import urlencode
from common import tool, tornado_timmer
import validate
import config

target_page_struct_list = config.crawler_setting["proxy.us-proxy.org"]["target_page_struct_list"]
collection_name = config.crawler_setting["proxy.us-proxy.org"]["collection_name"]
data_source = config.crawler_setting["proxy.us-proxy.org"]["data_source"]


@gen.coroutine
def crawler_page_html(page_url, retry=True):

    # raise gen.Return( open("test.html", "rb").read() )   # DEBUG
    req_data = {
        "url": page_url,
        "method": "GET",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        },
        "proxy_host": None,
        "proxy_port": None,
        "request_timeout": 30,
    }
    response = yield tool.http_request(req_data)
    if response.code == 599 and retry:
        raise Exception("http status code %s,%s" % (response.code, response.error))
        response = yield tool.http_request(req_data)

    if response.code != 200:
        raise gen.Return("")

    raise gen.Return(response.body)


def construct_page_url_string(target_page_struct, page):
    return target_page_struct # % page


def grep_page_ip_list(page_html):
    retult = []
    ip_table = page_html.xpath("//tbody")[0]
    ip_trs = ip_table.xpath("tr")
    return [ [ td.xpath("string()").strip() for td in tr.xpath("td") ] for tr in ip_trs ]


def convert_ip_list_format(ip_list):
    retult_list = []
    for item in ip_list:
        try:
            retult_list.append({
                "proxy_host": item[0],
                "proxy_port": float(item[1]),
                "proxy_username": None,
                "proxy_password": None,

                "location": None,
                "delay": None,
                "create_datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_validate_datetime": None,

                "a_https": None,
                "a_post": None,

                "anoy": None,

                "score": 0,
                "data_source": data_source,
            })
        except Exception as e:
            print item
            print traceback.format_exc()
            pass

    return retult_list


@gen.coroutine
def save_to_db(mongodb, ip_data):

    try:
        insert_result = yield mongodb[collection_name].insert(ip_data)
    except Exception, e:
        print traceback.format_exc()
    else:
        print "insert_result len:", len(insert_result)


@gen.coroutine
def do(mongodb):

    print "Job proxy_us_proxy_org start at %s!" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    yield mongodb[collection_name].aggregate([{
        "$out": "%s_bak" % collection_name
    }]).to_list(length=None)
    yield mongodb[collection_name].remove({})

    for target_page_base in target_page_struct_list:

        start_page = int(target_page_base[1])
        start_page_url = construct_page_url_string(target_page_base[0], start_page)

        start_page_html = yield crawler_page_html(start_page_url, True)
        start_page_html = etree.HTML(start_page_html)
        ip_list = grep_page_ip_list(start_page_html)

        ip_data = convert_ip_list_format(ip_list)

        yield save_to_db(mongodb, ip_data)

    # 验证代理ip是否有效
    yield validate.do(mongodb, collection_name, data_source)

    print "Job proxy_us_proxy_org done at %s!" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
