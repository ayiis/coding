# coding=utf8
import tornado.gen

from modules import (
    ws_jingdong,
    ws_douban,
)


from common import tornado_timmer
from common.mongodb import DBS
from conf import config


@tornado.gen.coroutine
def do_return_sequence_name(handler, req_data):
    sequence_name = yield DBS["db_test"].get_next_sequence("sequence_counters")
    raise tornado.gen.Return({"sequence_name": sequence_name})


@tornado.gen.coroutine
def init():

    yield ws_douban.execute()
    # yield ws_jingdong.execute()

    raise tornado.gen.Return(True)

    if config.WATCH_DOGS["jingdong"]["enable"]:
        tornado_timmer.set_interval(config.WATCH_DOGS["jingdong"]["period"], ws_jingdong.execute)

    if config.WATCH_DOGS["douban"]["enable"]:
        tornado_timmer.set_interval(config.WATCH_DOGS["douban"]["period"], ws_douban.execute)


