#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import re

import tornado
from tornado import gen
from common import tool
import datetime

HTTPS_URL = "https://apis.google.com/js/api.js"
# HTTPS_URL = "https://accounts.google.com/o/oauth2/postmessageRelay"


def construct_gfw(proxy_host, proxy_port, timeout):
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


@gen.coroutine
def do_validate(req, my_ip, proxy_host, proxy_port):

    http_get_response = yield req
    if http_get_response.code != 200:
        raise gen.Return(False)

    raise gen.Return( http_get_response.body[:32] == "var gapi=window.gapi=window.gapi")


@gen.coroutine
def validate(proxy_host, proxy_port, my_ip=None, timeout=30):

    # validate gfw by https get
    gfw = construct_gfw(proxy_host, proxy_port, timeout)

    gfw_status = yield do_validate(gfw, my_ip, proxy_host, proxy_port)
    if gfw_status == True:
        raise gen.Return(True)

    raise gen.Return(False)
