#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen
from common.mongodb import DBS


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("get: Hello, world")

    def post(self):
        self.write("post: Hello, world")


@tornado.gen.coroutine
def do_return_ok(handler, req_data):
    req_data["answer"] = "by server"
    raise tornado.gen.Return({"receive": req_data, "ok": True})


@tornado.gen.coroutine
def do_return_sequence_name(handler, req_data):
    sequence_name = yield DBS["db_test"].get_next_sequence("sequence_counters")
    raise tornado.gen.Return({"sequence_name": sequence_name})


@tornado.gen.coroutine
def do_return_error(handler, req_data):
    assert "key" in req_data, "You are not qualified"
    raise tornado.gen.Return({"pass": True})
