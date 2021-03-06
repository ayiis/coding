#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import re

import tornado
from tornado import gen, ioloop, httpclient
from urllib import urlencode
from common import tool, tornado_timmer
import datetime

from proxy_crawler import (
    validate_google as default_gfw_validate_site,
)

from common import my_logger
logging = my_logger.Logger("proxy_crawler.validate_ayiis_me.py", False, True, True)

URL = "http://wodove.com/ip"
HTTPS_URL = "https://wodove.com/ip"


def construct_http_get(proxy_host, proxy_port, timeout):

    return tool.http_request({
        "url": URL,
        "method": "GET",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
        },
        "body": None,
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "request_timeout": timeout,
    })


def construct_https_get(proxy_host, proxy_port, timeout):
    return tool.http_request({
        "url": HTTPS_URL,
        "method": "GET",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
        },
        "body": None,
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "request_timeout": timeout,
    })


def construct_http_post(proxy_host, proxy_port, timeout):
    return tool.http_request({
        "url": URL,
        "method": "POST",
        "headers": {
            "Content-Length": "17",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
        },
        "body": "username=bogeming",
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "request_timeout": timeout,
    })

def construct_https_post(proxy_host, proxy_port, timeout):
    return tool.http_request({
        "url": HTTPS_URL,
        "method": "POST",
        "headers": {
            "Content-Length": "17",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
        },
        "body": "username=bogeming",
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "request_timeout": timeout,
    })


@gen.coroutine
def do_validate(req, my_ip, proxy_host, proxy_port):

    try:
        http_get_response = yield req
    except:
        logging.my_exc("Requset Error on:", proxy_host, proxy_port)
        raise gen.Return(-3)

    if http_get_response.code != 200:
        raise gen.Return(-1)

    res_body = http_get_response.body.strip()
    if not re.match("^[\d]+.[\d]+.[\d]+.[\d]+$", res_body):
        raise gen.Return(-2)

    raise gen.Return( my_ip not in res_body )


@gen.coroutine
def validate(proxy_host, proxy_port, my_ip=None, timeout=30):

    datetime_now = datetime.datetime.now()
    result = {
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "anoy": 0,
        "http_get": False,
        "https_get": False,
        "http_post": False,
        "https_post": False,
        "last_validate_datetime": datetime_now.strftime("%Y-%m-%d %H:%M:%S"),
        "delay": 0,
        "gfw": False,
    }

    # validate http get
    http_get = construct_http_get(proxy_host, proxy_port, timeout)
    if http_get:
        http_get_status = yield do_validate(http_get, my_ip, proxy_host, proxy_port)
        if http_get_status < 0:
            result["http_get"] = False
        else:
            result["http_get"] = True
            result["anoy"] = http_get_status
            result["delay"] = max( (datetime.datetime.now() - datetime_now).total_seconds(), result["delay"])

    datetime_now = datetime.datetime.now()

    # validate https get
    https_get = construct_https_get(proxy_host, proxy_port, timeout)
    if https_get and result["http_get"]:
        https_get_status = yield do_validate(https_get, my_ip, proxy_host, proxy_port)
        if https_get_status < 0:
            result["https_get"] = False
        else:
            result["https_get"] = True
            result["anoy"] = https_get_status
            result["delay"] = max( (datetime.datetime.now() - datetime_now).total_seconds(), result["delay"])

            # If https get is available, validate gfw
            result["gfw"] = yield default_gfw_validate_site.validate(proxy_host, proxy_port, my_ip, timeout)

    datetime_now = datetime.datetime.now()

    # validate http post
    http_post = construct_http_post(proxy_host, proxy_port, timeout)
    if http_post:
        http_post_status = yield do_validate(http_post, my_ip, proxy_host, proxy_port)
        if http_post_status < 0:
            result["http_post"] = False
        else:
            result["http_post"] = True
            result["anoy"] = http_post_status
            result["delay"] = max( (datetime.datetime.now() - datetime_now).total_seconds(), result["delay"])

    datetime_now = datetime.datetime.now()

    # validate https post
    https_post = construct_https_post(proxy_host, proxy_port, timeout)
    if https_post and result["http_post"]:
        https_post_status = yield do_validate(https_post, my_ip, proxy_host, proxy_port)
        if https_post_status < 0:
            result["https_post"] = False
        else:
            result["https_post"] = True
            result["anoy"] = https_post_status
            result["delay"] = max( (datetime.datetime.now() - datetime_now).total_seconds(), result["delay"])

    if result["http_get"] or result["https_get"] or result["http_post"] or result["https_post"]:
        raise gen.Return(result)
    else:
        raise gen.Return(None)
