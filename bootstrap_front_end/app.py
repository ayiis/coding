#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2019/01/01
"""
    https://stackoverflow.com/questions/10165665/how-to-serve-static-files-from-a-different-directory-than-the-static-path
    https://github.com/tornadoweb/tornado/blob/fc6dd2345c3c8af0186765fc0396ff70e47c3022/tornado/web.py#L2488
"""
import tornado.ioloop
import tornado.web
import tornado.gen

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("tornado.application")


@tornado.gen.coroutine
def make_app():

    from handlers import StaticHandler, TemplateHandler
    from build import build

    build("templates_jade", "templates")

    settings = {
        "template_path": "templates",
        "autoreload": True,
        "debug": False,
    }

    app = tornado.web.Application([
        # (.*) will pass the `request path` into the handler's get/post function, as an argument
        # ? why don't they just use `self.request.path`
        # Tornado use mimetypes.guess_type to obtain Content-Type so you'd better name them properly
        (r"/css/(.*)", StaticHandler, {"path": "static/css"}),
        (r"/js/(.*)", StaticHandler, {"path": "static/js"}),
        (r"/fonts/(.*)", StaticHandler, {"path": "static/fonts"}),
        (r"/img/(.*)", StaticHandler, {"path": "static/img"}),

        # {"root": "templates"} will pass into the handler's initialize function
        (r"/(.*)", TemplateHandler, {"root": "templates", "default_filename": "index"}),
    ], **settings)
    app.listen(11111)
    print("listening 11111")


if __name__ == "__main__":
    make_app()
    tornado.ioloop.IOLoop.current().start()
