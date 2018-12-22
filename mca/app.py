#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import tornado
import tornado.web
from tornado import ioloop, gen
from tornado.options import define, options

import traceback

import router, handler


@gen.coroutine
def init():

    try:

        yield handler.init()

        define("port", default=50082, help="run on the given port", type=int)
        options.parse_command_line()

        router.add_get_url_handlers({
            "/": "static/go_chatroom.html",
            "/chat": "static/go_chatroom.html",
            "/chatroom.html": "static/go_chatroom.html",
            "/comments.txt": "static/comments.txt",
        })
        router.add_post_url_handlers({
            "/staticapi/api/send_message": handler.send_message,
            "/staticapi/api/get_item_detail": handler.get_item_detail,
        })

        settings = {
            "debug": False,
            "autoreload": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
        }

        tornado.web.Application([
            (r"/add_one", handler.AddOne),
            (r"/save_new_item", handler.AddOne),
            (r"/.*", router.DefaultRouterHandler),  # 默认处理方法，其他处理方法需在此方法之前声明
            # (r".*", proxy.ProxyHandler),            # ProxyHandler
        ], **settings).listen(options.port)

        print("Listening:", options.port)

    except Exception:
        print(traceback.format_exc())
        raise


if __name__ == "__main__":
    init()
    ioloop.IOLoop.current().start()
