#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import tornado, tornado.gen
import traceback


class WorkerPool(object):

    def __init__(self, args):

        super(WorkerPool, self).__init__()

        self.settings = {
            "func": args["func"] or (lambda: None),
            "pool_size": args["pool_size"],

            # default
            "exited": False,
            "stopped": False,
            "working": 0,
            "done": 0,
        }

    # mark as stoped, stop fork new job
    def stop(self):

        self.settings["stopped"] = True

    # mark as exited, wait for the last fork job done
    def exit(self):

        self.settings["exited"] = True

    # debuging issues
    @tornado.gen.coroutine
    def debug_pring(self):

        yield tornado.gen.sleep(1)

        print {x: self.settings[x] for x in self.settings if x not in ("func", "stop_condition", "exit_condition")}

        if not self.settings["exited"]:
            self.debug_pring()

    @tornado.gen.coroutine
    def fork_function(self):

        self.settings["working"] += 1

        try:
            # fork target function with this
            yield self.settings["func"](self)
        except Exception:
            print traceback.format_exc()

        self.settings["working"] -= 1

        self.settings["done"] += 1

    @tornado.gen.coroutine
    def start_pool(self):

        # print worker status
        # self.debug_pring()

        # when to stop
        while not self.settings["exited"]:

            # if not stop and there is available worker [pool_size - working]
            if not self.settings["stopped"] and self.settings["working"] < self.settings["pool_size"]:

                # do create workers
                self.fork_function()

            else:

                # waiting for worker getting it's job done
                yield tornado.gen.sleep(0.1)

        print "DONE!"


#
#
#
#
#
#
st = {
    "stop": False,
    "total": 0,
    "done": 0,

    "db": None,
    "ObjectId": None,
    "page_size": None,

    "data_list": [],
    "generate_next_hold": False,

}


def get_next_data():

    if st["ObjectId"]:
        find_req = {
            "_id": {
                "$gt": st["ObjectId"]
            }
        }
    else:
        find_req = {}

    return st["db"].find(find_req, {
        "proxy_host" : 1,
        "proxy_port" : 1,
    }).sort([("_id", 1)]).limit(st["page_size"]).to_list(length=None)


@tornado.gen.coroutine
def generate_next(pool):

    while st["generate_next_hold"]: yield tornado.gen.sleep(0.1)

    if not st["data_list"] and not st["stop"]:

        st["generate_next_hold"] = True
        st["data_list"] = yield get_next_data()
        st["generate_next_hold"] = False

        print 'st["data_list"]:', len(st["data_list"])
        if st["data_list"]:
            st["total"] += len(st["data_list"])
            st["ObjectId"] = st["data_list"][-1]["_id"]
        else:
            # shall be stop
            st["stop"] = True

    if not st["stop"]:
        raise tornado.gen.Return(st["data_list"].pop())
    else:
        # will be call many time
        pool.stop()
        raise tornado.gen.Return(None)


@tornado.gen.coroutine
def fork(pool):

    proxy_item = yield generate_next(pool)

    if proxy_item:

        yield do_check_available(proxy_item)

        st["done"] = st["done"] + 1

        print {x:st[x] for x in st if x not in ("data_list", "db") }

    # exit pool
    if st["stop"] and st["done"] == st["total"]:
        pool.exit()


@tornado.gen.coroutine
def do_check_available(proxy_item):
    pass
    # print "item:", proxy_item


@tornado.gen.coroutine
def do(db):

    st["db"] = db
    st["page_size"] = 100

    pool = tornado_pool.WorkerPool({
        "func": fork,
        "pool_size": 50,
    })

    yield pool.start_pool()
