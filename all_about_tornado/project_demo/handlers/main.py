#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("get: Hello, world")

    def post(self):
        self.write("post: Hello, world")
