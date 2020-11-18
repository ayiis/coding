# coding=utf8
import tornado.gen

from modules import (
    ws_jingdong,
    ws_douban,
    ws_kaola,
    ws_yanxuan,
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

    # yield ws_jingdong.execute()
    # exit(1)

    # yield ws_douban.execute()
    # yield ws_kaola.execute()
    # yield ws_yanxuan.execute()

    # def aaa():
    #     import time
    #     print("this is:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    # tornado_timmer.MinuteTimmer(aaa)

    # exit(1)

    # exit(1)
    # raise tornado.gen.Return(True)

    if config.WATCH_DOGS["jingdong"]["enable"]:
        # tornado_timmer.set_interval(config.WATCH_DOGS["jingdong"]["period"], ws_jingdong.execute)
        tornado_timmer.MinuteTimmer(ws_jingdong.execute, config.WATCH_DOGS["jingdong"]["minute_list"])

    if config.WATCH_DOGS["kaola"]["enable"]:
        # tornado_timmer.set_interval(config.WATCH_DOGS["kaola"]["period"], ws_kaola.execute)
        tornado_timmer.MinuteTimmer(ws_kaola.execute, config.WATCH_DOGS["kaola"]["minute_list"])

    if config.WATCH_DOGS["yanxuan"]["enable"]:
        # tornado_timmer.set_interval(config.WATCH_DOGS["yanxuan"]["period"], ws_yanxuan.execute)
        tornado_timmer.MinuteTimmer(ws_yanxuan.execute, config.WATCH_DOGS["yanxuan"]["minute_list"])

    if config.WATCH_DOGS["douban"]["enable"]:
        tornado_timmer.set_interval(config.WATCH_DOGS["douban"]["period"], ws_douban.execute)


