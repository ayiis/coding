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
import tornado.httpclient
import tornado.httputil


ProxyList = {}


def GetProxy(name):
    return ProxyList[name]


class ProxyManager(object):


    def __init__(self, arg):

        print "arg:", arg

        if arg.get("name", "default") in ProxyList:
            return ProxyList[ arg.get("name", "default") ]

        super(ProxyManager, self).__init__()
        self.arg = arg
        self.setting = {
            "proxy_list": None,
            "ObjectId": None,
            "cache_size": arg.get("cache_size") or 100,
            "collection": arg["collection"],
            "unavailable_collection": arg["unavailable_collection"],
        }

        ProxyList[arg["name"]] = self


    def grep_proxy_from_db(self):

        if self.setting["ObjectId"]:
            find_req = {
                "anoy": True,
                "_id": {
                    "$gt": self.setting["ObjectId"]
                }
            }
        else:
            find_req = {
                "anoy": True,
            }

        print self.setting["collection"]
        print find_req

        return self.setting["collection"].find(find_req, {
            "proxy_host": 1,
            "proxy_port": 1,
            "data_source": 1,
        }).sort([("_id", 1)]).limit(self.setting["cache_size"]).to_list(length=None)


    @tornado.gen.coroutine
    def get_a_proxy(self):
        if not self.setting["proxy_list"]:
            self.setting["proxy_list"] = yield self.grep_proxy_from_db()

        if not self.setting["proxy_list"]:
            raise Exception("No available proxy..")

        raise tornado.gen.Return( self.setting["proxy_list"].pop() )


    @tornado.gen.coroutine
    def disable_a_proxy(self, proxy_item):

        # move to unavailable_pool
        yield [
            self.setting["collection"].remove({"_id": proxy_item["_id"]}),
            self.setting["unavailable_collection"].insert(proxy_item),
        ]
