# coding=utf8

import tornado
import tornado.gen
import tornado.httpclient

import check_available
import check_unavailable
import check_fail

import config
from common import tornado_timmer

@tornado.gen.coroutine
def init(db):

    tornado_timmer.set_interval(config.setting["available_pool"]["period"], lambda: check_available.do(db))
    # yield check_available.do(db)

    tornado_timmer.set_interval(config.setting["unavailable_pool"]["period"], lambda: check_unavailable.do(db))
    # yield check_unavailable.do(db)

    tornado_timmer.set_interval(config.setting["fail_pool"]["period"], lambda: check_fail.do(db))
    # yield check_fail.do(db)
