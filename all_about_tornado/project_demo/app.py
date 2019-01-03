#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    https://stackoverflow.com/questions/10165665/how-to-serve-static-files-from-a-different-directory-than-the-static-path
    https://github.com/tornadoweb/tornado/blob/fc6dd2345c3c8af0186765fc0396ff70e47c3022/tornado/web.py#L2488
"""
import tornado.ioloop
import tornado.web

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("tornado.application")


def make_app():

    from handlers import TemplateHandler, main
    from build import build

    build("templates_jade", "templates")

    settings = {
        "template_path": "templates",
        "autoreload": True,
        "debug": True,
    }

    app = tornado.web.Application([
        (r"/main", main.MainHandler),

        # tornado use mimetypes.guess_type to obtain Content-Type so you should name them properly
        (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": "static/css"}),
        (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": "static/js"}),
        (r"/img/(.*)", tornado.web.StaticFileHandler, {"path": "static/img"}),

        # (.*) will pass the request PATH into the handler's get/post function
        # {"root": "templates"} will pass into the handler's initialize function
        (r"/(.*)", TemplateHandler, {"root": "templates", "default_filename": "index"}),
    ], **settings)
    app.listen(8888)
    print("listening 8888")


if __name__ == "__main__":
    make_app()
    tornado.ioloop.IOLoop.current().start()
