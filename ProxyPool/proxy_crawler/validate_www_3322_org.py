#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import re
import re

import tornado
from tornado import gen, ioloop, httpclient
from urllib import urlencode
from common import tool, tornado_timmer

URL = "http://www.3322.org/dyndns/getip"
REQUEST_TIMEOUT = 30

def construct_http_get(proxy_host, proxy_port):
    return tool.http_request({
        "url": URL,
        "method": "GET",
        "headers": {
            # "Via": "none",
            # "X-Forwarded-For": proxy_host,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
        },
        "body": None,
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "request_timeout": REQUEST_TIMEOUT,
    })


def construct_https_get(proxy_host, proxy_port):
    return None


def construct_http_post(proxy_host, proxy_port):
    return tool.http_request({
        "url": URL,
        "method": "POST",
        "headers": {
            # "Via": "none",
            # "X-Forwarded-For": proxy_host,
            "Content-Length": "17",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3282.119 Safari/537.36",
        },
        "body": "username=bogeming",
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "request_timeout": REQUEST_TIMEOUT,
    })


def construct_https_post(proxy_host, proxy_port):
    return None



@gen.coroutine
def analyze_response(yield_list_id, yield_list):
    yield_list_result = yield yield_list
    for index, proxy_host in enumerate(yield_list_id):
        response = yield_list_result[index]
        if response.code != 200:
            open("bad_result.json", "a").write("%s\r\n" % (proxy_host))
            continue
        elif response.body.strip() not in proxy_host:
            print "200 but. %s not in %s:" % (proxy_host, response.body)
            open("warning_result.json", "a").write("%s in %s\r\n" % (proxy_host, response.body))
            continue
        else:
            print "GOOD!"
            print "%s in %s:", proxy_host, response.body
            open("good_result.json", "a").write("%s in %s\r\n" % (proxy_host, response.body))


@gen.coroutine
def do_validate(req, my_ip):

    http_get_response = yield req
    if http_get_response.code != 200:
        raise gen.Return(-1)

    res_body = http_get_response.body.strip()
    if not re.match("^[\d]+.[\d]+.[\d]+.[\d]+$", res_body):
        raise gen.Return(-2)

    raise gen.Return( my_ip not in res_body )


@gen.coroutine
def validate(proxy_host, proxy_port, my_ip=None):

    result = {
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "anoy": 0,
        "http_get": False,
        "https_get": False,
        "http_post": False,
        "https_post": False,
    }

    # validate http get
    http_get = construct_http_get(proxy_host, proxy_port)
    if http_get:
        http_get_status = yield do_validate(http_get, my_ip)
        if http_get_status < 0:
            result["http_get"] = False
        else:
            result["http_get"] = True
            result["anoy"] = http_get_status

    # validate https get
    https_get = construct_https_get(proxy_host, proxy_port)
    if https_get and result["http_get"]:
        https_get_status = yield do_validate(https_get, my_ip)
        if https_get_status < 0:
            result["https_get"] = False
        else:
            result["https_get"] = True
            result["anoy"] = https_get_status

    # validate http post
    http_post = construct_http_post(proxy_host, proxy_port)
    if http_post:
        http_post_status = yield do_validate(http_post, my_ip)
        if http_post_status < 0:
            result["http_post"] = False
        else:
            result["http_post"] = True
            result["anoy"] = http_post_status

    # validate https post
    https_post = construct_https_post(proxy_host, proxy_port)
    if https_post and result["http_post"]:
        https_post_status = yield do_validate(https_post, my_ip)
        if https_post_status < 0:
            result["https_post"] = False
        else:
            result["https_post"] = True
            result["anoy"] = https_post_status

    if result["http_get"] or result["https_get"] or result["http_post"] or result["https_post"]:
        raise gen.Return(result)
    else:
        raise gen.Return(None)
