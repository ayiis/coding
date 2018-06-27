#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# 解决uft-8中文序列化报错的问题
import sys
reload(sys).setdefaultencoding("utf-8")

import tornado
import tornado.gen
import tornado.web
from tornado.options import define
from tornado.options import options

from common import my_mongodb
from common import my_logger
import schedules
import config

from routes import router
from routes import proxy
from routes import proxy_manager

logging = my_logger.Logger("app.py", True, True, True)


@tornado.gen.coroutine
def main():

    try:

        define("port", default=config.SYSTEM["listening_port"], help="run on the given port", type=int)
        options.parse_command_line()

        mongodbs = yield my_mongodb.init(config.MONGODB)
        proxy_manager.ProxyManager({
            "name": "default",
            "cache_size": 200,
            # "anoy": True,
            "collection": mongodbs["DB_PROXY_POOL"]["available_pool"],
            "unavailable_collection": mongodbs["DB_PROXY_POOL"]["unavailable_pool"],
        })

        yield schedules.init(mongodbs["DB_PROXY_POOL"])

        settings = {
            # "debug": True,
            # "autoreload": True,
        }
        # settings.update(mongodbs)

        tornado.web.Application([
            (r"/.*", router.DefaultRouterHandler),  # 默认处理方法，其他处理方法需在此方法之前声明
            (r".*", proxy.ProxyHandler),            # ProxyHandler
        ], **settings).listen(options.port)

    except Exception as e:
        logging.my_exc("start fail.")
        tornado.ioloop.IOLoop.current().stop()
    else:
        logging.info("[SUCCESS] listening %s" % options.port)


@tornado.gen.coroutine
def test():
    from proxy_crawler import proxy_freeproxylists_net
    from proxy_crawler import validate

    mongodbs = yield my_mongodb.init(config.MONGODB)

    yield proxy_freeproxylists_net.do(mongodbs["DB_PROXY_POOL"])

    # yield validate.do(mongodbs["DB_PROXY_POOL"], "proxy.freeproxylists.net.ip_date_raw", "www.freeproxylists.net")

    print "DONE."

    tornado.ioloop.IOLoop.current().stop()


# 启动api
if __name__ == "__main__":
    try:
        test()
        # main()
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        logging.my_exc("start fail.")
