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

    from handlers import StaticHandler, TemplateHandler, ApiHandler
    from build import build

    build("templates_jade", "templates")

    from common import mongodb
    from conf import config

    yield mongodb.init(config.MONGODB)

    from modules import init_schedules
    yield init_schedules.init()

    settings = {
        "template_path": "templates",
        # "autoreload": False,
        "autoreload": True,
        "debug": False,
    }

    from handlers import main, watchdog
    from handlers import rent_douban, jingdong

    ApiHandler.update_url_handlers({
        "/api/200": main.do_return_ok,
        "/api/500": main.do_return_error,
        "/api/get_sequence_name": main.do_return_sequence_name,

        "/api/watchdog/add": watchdog.add,
        "/api/jingdong/task_add": jingdong.task_add,
        "/api/jingdong/task_list": jingdong.task_list,
        "/api/jingdong/task_update_status": jingdong.task_update_status,

        "/api/rent/task_list": rent_douban.task_list,
        "/api/rent/query_filter": rent_douban.query_filter,
        "/api/rent/change_filter": rent_douban.change_filter,
    })

    app = tornado.web.Application([
        (r"/main", main.MainHandler),

        # (.*) will pass the `request path` into the handler's get/post function, as an argument
        # ? why don't they just use `self.request.path`
        # Tornado use mimetypes.guess_type to obtain Content-Type so you'd better name them properly
        (r"/css/(.*)", StaticHandler, {"path": "static/css"}),
        (r"/js/(.*)", StaticHandler, {"path": "static/js"}),
        (r"/img/(.*)", StaticHandler, {"path": "static/img"}),

        (r"/api/.*", ApiHandler),

        # {"root": "templates"} will pass into the handler's initialize function
        (r"/(.*)", TemplateHandler, {"root": "templates", "default_filename": "index"}),
    ], **settings)
    app.listen(config.SYSTEM["listening_port"])
    print("listening %s" % config.SYSTEM["listening_port"])


if __name__ == "__main__":
    make_app()
    # from modules import watchdog_amobbs
    # watchdog_amobbs.main()
    tornado.ioloop.IOLoop.current().start()
