#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import json
import datetime
import re
import time
import decimal
import hashlib
import base64
import traceback
import zlib

from Crypto.Cipher import AES, DES
from bson.objectid import ObjectId

import config


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
            return time.strftime("%H:%M:%S", time.localtime(obj.seconds + 60 * 60 * (24 - 8))) # hacked
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


def wrap_unicode(data):
    if isinstance(data, dict):
        return {wrap_unicode(key): wrap_unicode(value) for key, value in data.iteritems()}
    elif isinstance(data, list):
        return [wrap_unicode(element) for element in data]
    elif isinstance(data, unicode):
        return data.encode("utf-8")
    else:
        return data


def json_stringify(data):
    return json.dumps(wrap_unicode(data), cls=MyEncoder, encoding="utf-8", ensure_ascii=False)


def json_load(data):
    return wrap_unicode(json.loads(data))


def getMd5Base64(val):
    val = val.encode("utf8")
    hash = hashlib.md5()
    hash.update(val)
    return base64.encodestring(hash.digest()).rstrip()


def get_md5_digest(text):
    return hashlib.md5( "%s:%s" % (text, config.SECRET["md5_salt"])).digest()


# BS = 16
unpad_pkcs5 = lambda s: s[0:-ord(s[-1])]


def aes_decrypt(text, key, iv):
    # 解密字符串
    return AES.new(key, AES.MODE_CBC, iv).decrypt(base64.b64decode(text))


def encrypt(text, key, iv):
    # 加密字符串
    return base64.b64encode(AES.new(key, AES.MODE_CBC, iv).encrypt(text + ("\0" * (16 - (len(text) % 16)))))


def decrypt(text, key, iv):
    # 解密字符串
    return AES.new(key, AES.MODE_CBC, iv).decrypt(base64.b64decode(text)).rstrip("\0")


def gzip_decode(g_data):
    return zlib.decompress(g_data, zlib.MAX_WBITS | 32)


def my_encrypt(username, password, data):
    key = hashlib.md5(text).digest(username)
    iv = hashlib.md5(text).digest(password)

    return encrypt(data, key, iv)


# 精确到亿 999999999
def fixed_float(num, fixed=2):
    return round(float("%fe-%s" % (round(float("%fe+%s" % (num, fixed )), 0), fixed)), fixed)


import tornado.httpclient
tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
async_http_client = tornado.httpclient.AsyncHTTPClient(max_clients=2000)

def http_request(req_data, **kwargs):
    return async_http_client.fetch(tornado.httpclient.HTTPRequest(
        url=req_data["url"],
        method=req_data["method"],
        headers=req_data["headers"],
        body=req_data.get("body"),
        decompress_response=True,
        proxy_host=req_data.get("proxy_host"),
        proxy_port=req_data.get("proxy_port"),
        request_timeout=req_data.get("request_timeout") or 30,
        connect_timeout=req_data.get("request_timeout") or 30,
        **kwargs
    ), raise_error=False)


def get_my_ip():
    return "59.42.106.170"
