#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    http://stackoverflow.com/questions/18307131/how-to-create-https-tornado-server
"""

import tornado.httpserver
import tornado.ioloop
import tornado.web


class getToken(tornado.web.RequestHandler):
    def get(self):
        self.write("hello")


application = tornado.web.Application([
    (r"/", getToken),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": "/var/pyTest/keys/ca.csr",
        "keyfile": "/var/pyTest/keys/ca.key",
    })
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()
