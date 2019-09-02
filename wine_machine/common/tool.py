#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import datetime
from datetime import timedelta
import re
import time
import decimal
import hashlib
import base64
import traceback
import zlib

from bson.objectid import ObjectId
from urllib.parse import urlencode, quote_plus
from inspect import getframeinfo, stack


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj == datetime.datetime.min:
                return None
            else:
                return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            if obj == datetime.date.min:
                return None
            else:
                return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.timedelta):
            return time.strftime("%H:%M:%S", time.localtime(obj.seconds + 60 * 60 * (24 - 8)))  # hacked
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        # elif isinstance(obj, enum.Enum):
        #     return obj.value
        elif isinstance(obj, Exception):
            return {
                "error": obj.__class__.__name__,
                "args": obj.args,
            }
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def json_stringify(data, **args):
    return json.dumps(data, cls=MyEncoder, ensure_ascii=False, **args)


def json_load(data):
    return json.loads(data)


def gzip_decode(g_data):
    return zlib.decompress(g_data, zlib.MAX_WBITS | 32)


# 精确到亿 999999999
def fixed_float(num, fixed=2):
    return round(float("%fe-%s" % (round(float("%fe+%s" % (num, fixed )), 0), fixed)), fixed)


import tornado.httpclient
# tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
async_http_client = tornado.httpclient.AsyncHTTPClient(max_clients=2000)


def http_request(req_data, **kwargs):
    return async_http_client.fetch(tornado.httpclient.HTTPRequest(
        url=req_data["url"],
        method=req_data["method"],
        headers=req_data["headers"],
        body=req_data.get("body"),
        decompress_response=True,
        # proxy_host=req_data.get("proxy_host"),
        # proxy_port=req_data.get("proxy_port"),
        request_timeout=req_data.get("request_timeout") or 30,
        connect_timeout=req_data.get("request_timeout") or 30,
        # validate_cert=False,
        # allow_nonstandard_methods=True,
        **kwargs
    ), raise_error=False)


def get_my_ip():
    return "59.42.106.170"


def send_to_my_wx(text, desp):
    return http_request({
        "url": "https://ayiis.me/.send",
        "method": "POST",
        "headers": {},
        "request_timeout": 16,
        "body": "text=%s&desp=%s" % (quote_plus(text), quote_plus(desp))
    })


def aprint(*args):
    caller = getframeinfo(stack()[1][0])
    date_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    caller_string = "%s@%s:" % (caller.filename, caller.lineno)
    return print(date_string, caller_string, *args)


def get_datetime_string():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date_string():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_date(date_type, strftime="%Y-%m-%d"):
    now = datetime.datetime.now()
    if date_type == "today":
        target_date = now
    elif date_type == "week_start":
        target_date = now - timedelta(days=now.weekday())
    elif date_type == "week_end":
        target_date = now + timedelta(days=6 - now.weekday())
    elif date_type == "month_start":
        target_date = datetime.datetime(now.year, now.month, 1)
    elif date_type == "month_end":
        target_date = datetime.datetime(now.year, now.month + 1, 1) - timedelta(days=1)
    elif date_type == "year_start":
        target_date = datetime.datetime(now.year, 1, 1)
    elif date_type == "year_end":
        target_date = datetime.datetime(now.year + 1, 1, 1) - timedelta(days=1)

    return target_date.strftime(strftime)
