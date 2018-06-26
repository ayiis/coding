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

        print {x:self.settings[x] for x in self.settings if x not in ("func", "stop_condition", "exit_condition") }

        if not self.settings["exited"]: self.debug_pring()


    @tornado.gen.coroutine
    def fork_function(self):

        self.settings["working"] += 1

        try:
            # fork target function with this
            yield self.settings["func"](self)
        except Exception, e:
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
