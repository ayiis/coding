#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import logging
import os
import sys
import socket
from urlparse import urlparse

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.httputil
import traceback

import proxy_manager
from common import tool

logger = logging.getLogger('tornado_proxy')

__all__ = ['ProxyHandler', 'run_proxy']


class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'CONNECT']
    ERROR_STATUS_CODE = 305 # FAIL TO BUILD CONNECTION

    def initialize(self):
        self.proxy_item = None

    def compute_etag(self):
        return None # disable tornado Etag

    @tornado.gen.coroutine
    def set_new_proxy(self):
        try:
            self.proxy_item = yield proxy_manager.GetProxy("default").get_a_proxy()
        except Exception, e:
            print traceback.format_exc()

    @tornado.gen.coroutine
    def construct_request(self):

        yield self.set_new_proxy()

        if self.proxy_item:
            logger.debug('Forward request via upstream proxy %s', self.proxy_item)
            # print "using:", self.proxy_item

            # Changing the `X-Forwarded-For`, works for some cases
            if self.proxy_item["anoy"] != True:
                self.request.headers["Via"] = "None"
                self.request.headers["X-Forwarded-For"] = self.proxy_item['proxy_host']

            raise tornado.gen.Return( tool.http_request({
                "url": self.request.uri,
                "method": self.request.method,
                "headers": self.request.headers,
                "body": self.request.body or None,
                "proxy_host": self.proxy_item['proxy_host'],
                "proxy_port": self.proxy_item['proxy_port'],
                "request_timeout": 15,
                "follow_redirects": False,
                "allow_nonstandard_methods": True
            }) )
        else:
            self.set_status(self.ERROR_STATUS_CODE)
            self.finish("Proxy server error:\n No available proxy.")

            raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def fetch_request(self, retry):
        request = yield self.construct_request()
        if request:
            response = yield request
            # print "response:", response
            if ( response.error and not isinstance(response.error, tornado.httpclient.HTTPError) ) or response.code >= 500:
                if retry > 0:
                    print "Warning: try next proxy."
                    yield proxy_manager.GetProxy("default").disable_a_proxy(self.proxy_item)
                    yield self.fetch_request(retry - 1)
                    raise tornado.gen.Return( None )
                else:
                    yield proxy_manager.GetProxy("default").disable_a_proxy(self.proxy_item)
                    self.set_status(self.ERROR_STATUS_CODE)
                    self.finish("Internal server error:\n" + str(response.error))
            else:
                self.set_status(response.code, response.reason)
                self._headers = tornado.httputil.HTTPHeaders() # clear tornado default header

                for header, v in response.headers.get_all():
                    if header not in ("Content-Length", "Transfer-Encoding", "Content-Encoding", "Connection"):
                        self.add_header(header, v) # some header appear multiple times, eg "Set-Cookie"

                if response.body:
                    self.set_header("Content-Length", len(response.body))
                    self.finish(response.body)
                else:
                    self.finish()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        logger.debug("Handle %s request to %s", self.request.method, self.request.uri)

        # print "self.request.headers:", self.request.headers
        if "Proxy-Connection" in self.request.headers:
            del self.request.headers["Proxy-Connection"]

        try:
            yield self.fetch_request(retry=1)
        except Exception, e:
            print traceback.format_exc()
            self.finish("Unexpected Error: %s" % e)

    @tornado.web.asynchronous
    def post(self):
        return self.get()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def connect(self):
        logger.debug('Start CONNECT to %s', self.request.uri)
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        def read_from_client(data):
            upstream.write(data)

        def read_from_upstream(data):
            client.write(data)

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()

        def start_tunnel():
            logger.debug('CONNECT tunnel established to %s', self.request.uri)
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        def on_proxy_response(data=None):
            if data:
                first_line = data.splitlines()[0]
                http_v, status, text = first_line.split(None, 2)
                if int(status) == 200:
                    logger.debug('Connected to upstream proxy %s', self.proxy_item)
                    start_tunnel()
                    return

            self.set_status(self.ERROR_STATUS_CODE)
            self.finish()

        def start_proxy_tunnel():
            upstream.write('CONNECT %s HTTP/1.1\r\n' % self.request.uri)
            upstream.write('Host: %s\r\n' % self.request.uri)
            upstream.write('Proxy-Connection: Keep-Alive\r\n\r\n')
            upstream.read_until('\r\n\r\n', on_proxy_response)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)

        yield self.set_new_proxy()
        if self.proxy_item:
            upstream.connect((self.proxy_item['proxy_host'], self.proxy_item['proxy_port']), start_proxy_tunnel)
        else:
            upstream.connect((host, int(port)), start_tunnel)


def run_proxy(port):
    """
    Run proxy on the specified port
    """
    settings = {
        "debug": True,
        "autoreload": True,
    }
    app = tornado.web.Application([
        (r'.*', ProxyHandler),
    ], **settings)

    app.listen(port)

    print "Listening %s" % port
