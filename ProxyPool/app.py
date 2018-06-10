#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# 解决uft-8中文序列化报错的问题
import sys
reload(sys).setdefaultencoding("utf-8")

import tornado, tornado.gen, tornado.web
from tornado.options import define, options
import datetime, traceback, os

import config
from common import (
    my_redis,
    my_mongodb,
    user,
)
from routes import (
    add_get_url_handlers,
    add_post_url_handlers,
    DefaultRouterHandler,
    user,
    note,
    log,
)

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("tornado.application")

add_get_url_handlers({
    "/": "deny.html",
    "/login": "login.html",
    "/account": "account.html",
    "/profile": "account.html",
    "/records": "records.html",
    "/notes": "notes.html",
    "/note_create": "note_create.html",
    "/note_edit": "note_edit.html",
    "/note_list": "note_list.html",
    "/test": "test.html",
    "/log": "log.html",
    "/password": "password.html",
})

add_post_url_handlers({
    "/user_login": user.login,
    "/user_logout": user.logout,
    "/user_change": user.change,
    "/user_create": user.create,
    "/user_delete": user.delete,

    "/note_create": note.create,
    "/note_edit": note.edit,
    "/note_list": note.list,
    "/note_query": note.query,

    "/log_list": log.list,
})


@tornado.gen.coroutine
def main():

    try:

        define("port", default=config.SYSTEM["api_port"], help="run on the given port", type=int)
        options.parse_command_line()

        yield my_mongodb.init()

        settings = {
            "debug": True,
            "autoreload": True,
        }

        tornado.web.Application([
            (r"/.*", DefaultRouterHandler)  # 默认处理方法，其他处理方法需在此方法之前声明
        ], **settings).listen(options.port)

    except Exception as e:
        print traceback.format_exc()
        tornado.ioloop.IOLoop.current().stop()
    else:
        print "[SUCCESS] listening %s" % options.port


# 启动api
if __name__ == "__main__":
    try:
        main()
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        print traceback.format_exc()
