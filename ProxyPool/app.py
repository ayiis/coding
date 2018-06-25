#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# 解决uft-8中文序列化报错的问题
import sys
reload(sys).setdefaultencoding("utf-8")

import tornado, tornado.gen, tornado.web
from tornado.options import define, options
import datetime, traceback, os

import config

import logging
logging.basicConfig(level=logging.ERROR)
logging.getLogger("tornado.application")

from common import my_mongodb


@tornado.gen.coroutine
def main():

    try:

        define("port", default=config.SYSTEM["api_port"], help="run on the given port", type=int)
        options.parse_command_line()

        settings = {
            "debug": True,
            "autoreload": True,
        }
        mongodbs = yield my_mongodb.init(config.MONGODB)
        settings.update(mongodbs)

        tornado.web.Application([
            (r"/.*", DefaultRouterHandler)  # 默认处理方法，其他处理方法需在此方法之前声明
        ], **settings).listen(options.port)

    except Exception as e:
        print traceback.format_exc()
        tornado.ioloop.IOLoop.current().stop()
    else:
        print "[SUCCESS] listening %s" % options.port


@tornado.gen.coroutine
def test_proxy_coderbusy_com():
    from proxy_crawler import proxy_coderbusy_com
    from proxy_crawler import validate
    try:
        print "START TEST"

        mongodbs = yield my_mongodb.init(config.MONGODB)

        # yield proxy_coderbusy_com.test(mongodbs["DB_PROXY_POOL"])
        yield validate.test(mongodbs["DB_PROXY_POOL"], "proxy.coderbusy.com.ip_date_raw", "proxy.coderbusy.com")

    except Exception, e:
        print traceback.format_exc()

    print "DONE"


@tornado.gen.coroutine
def test_proxy_xicidaili_com():
    from proxy_crawler import proxy_xicidaili_com
    from proxy_crawler import validate
    try:
        print "START TEST"

        mongodbs = yield my_mongodb.init(config.MONGODB)

        # yield proxy_xicidaili_com.test(mongodbs["DB_PROXY_POOL"])
        yield validate.test(mongodbs["DB_PROXY_POOL"], "www.xicidaili.com.ip_date_raw", "www.xicidaili.com")

    except Exception, e:
        print traceback.format_exc()

    print "DONE"


@tornado.gen.coroutine
def test_proxy_kuaidaili_com():
    from proxy_crawler import proxy_kuaidaili_com
    from proxy_crawler import validate
    try:
        print "START TEST"

        mongodbs = yield my_mongodb.init(config.MONGODB)

        yield proxy_kuaidaili_com.test(mongodbs["DB_PROXY_POOL"])

        # yield validate.test(mongodbs["DB_PROXY_POOL"], "www.kuaidaili.com.ip_date_raw", "www.kuaidaili.com")

    except Exception, e:
        print traceback.format_exc()

    print "DONE"


@tornado.gen.coroutine
def test_proxy_66ip_cn():
    from proxy_crawler import proxy_66ip_cn
    from proxy_crawler import validate
    try:
        print "START TEST"

        mongodbs = yield my_mongodb.init(config.MONGODB)

        yield proxy_66ip_cn.test(mongodbs["DB_PROXY_POOL"])

        # yield validate.test(mongodbs["DB_PROXY_POOL"], "www.66ip.cn.ip_date_raw", "www.66ip.cn")

    except Exception, e:
        print traceback.format_exc()

    print "DONE"


@tornado.gen.coroutine
def test_proxy_89ip_cn():
    from proxy_crawler import proxy_89ip_cn
    from proxy_crawler import validate
    try:
        print "START TEST proxy_89ip_cn"

        mongodbs = yield my_mongodb.init(config.MONGODB)

        yield proxy_89ip_cn.test(mongodbs["DB_PROXY_POOL"])

        # yield validate.test(mongodbs["DB_PROXY_POOL"], "www.89ip.cn.ip_date_raw", "www.89ip.cn")

    except Exception, e:
        print traceback.format_exc()

    print "DONE"


# 启动api
if __name__ == "__main__":
    try:
        # test_proxy_coderbusy_com()
        # test_proxy_xicidaili_com()
        # test_proxy_kuaidaili_com()
        # test_proxy_66ip_cn()
        test_proxy_89ip_cn()
        # main()
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        print traceback.format_exc()
