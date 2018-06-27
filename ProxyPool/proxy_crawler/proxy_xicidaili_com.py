#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import datetime, time
import re
import traceback
import json
import config
from lxml import etree

import tornado
from tornado import gen, ioloop, httpclient
from urllib import urlencode
from common import tool, tornado_timmer
import validate

target_page_struct_list = config.crawler_setting["proxy.xicidaili.com"]["target_page_struct_list"]
collection_name = config.crawler_setting["proxy.xicidaili.com"]["collection_name"]
data_source = config.crawler_setting["proxy.xicidaili.com"]["data_source"]


@gen.coroutine
def crawler_page_html(page_url, retry=True):

    req_data = {
        "url": page_url,
        "method": "GET",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
        },
        "proxy_host": None,
        "proxy_port": None,
        "request_timeout": 30,
    }
    response = yield tool.http_request(req_data)
    if response.code == 599 and retry:
        response = yield tool.http_request(req_data)

    if response.code != 200:
        # raise Exception("http status code %s,%s" % (response.code, response.error))
        raise gen.Return("")

    raise gen.Return(response.body)


def construct_page_url_string(target_page_struct, page):
    return target_page_struct % page


def grep_page_ip_list(page_html):
    ip_table = page_html.xpath("//table[@id=\"ip_list\"]")[0]
    ip_trs = ip_table.xpath("tr[position()>1]")
    return [ [ td.xpath("string()").strip() for td in tr.xpath("td") ] for tr in ip_trs ]


def grep_end_page(start_page_html):
    try:
        last_end = start_page_html.xpath(u"//div[@class=\"pagination\"]/a[last()-2]/text()")
        return int(last_end[0])
    except Exception as e:
        print traceback.format_exc()
        # 只有一页时，末页返回0
        return 0


def convert_ip_list_format(ip_list):
    retult_list = []
    for item in ip_list:
        try:
            retult_list.append({
                "proxy_host": item[1],
                "proxy_port": float(item[2]),
                "proxy_username": None,
                "proxy_password": None,

                "location": item[3],
                "delay": None,
                "create_datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_validate_datetime": None,

                "a_https": None,
                "a_post": None,

                "anoy": {
                    "透明": 0,
                    "匿名": 1,
                    "高匿名": 2,
                }.get(item[4], 0),

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

        end_page = int(grep_end_page(start_page_html))

        print "end_page is:", end_page

        if end_page > target_page_base[2]:
            end_page = target_page_base[2]

        for page in range(start_page +1, end_page +1):
            page_url = construct_page_url_string(target_page_base[0], page)
            print "working page:", page_url
            page_html = yield crawler_page_html(page_url, True)
            if not page_html:
                print "no page_html:", page_url
                yield tornado_timmer.sleep(1)
                continue
            page_html = etree.HTML(page_html)

            ip_list = grep_page_ip_list(page_html)
            ip_data = convert_ip_list_format(ip_list)
            yield save_to_db(mongodb, ip_data)

            # 防屏蔽，请求降频 | 或者使用代理提高频率
            yield tornado_timmer.sleep(5)

    ## 验证代理ip是否有效
    yield validate.do(mongodb, collection_name, data_source)
