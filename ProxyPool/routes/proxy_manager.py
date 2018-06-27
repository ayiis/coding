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

from common import my_logger
logging = my_logger.Logger("routes.proxy_manager.py", False, True, True)

ProxyList = {}


def GetProxy(name):
    return ProxyList.get(name) or None


class ProxyManager(object):


    def __init__(self, arg):
        super(ProxyManager, self).__init__()
        self.setting = {
            "proxy_list": None,
            "ObjectId": None,
            "anoy": arg.get("anoy") == True,
            "cache_size": arg.get("cache_size") or 100,
            "collection": arg["collection"],
            "unavailable_collection": arg["unavailable_collection"],
        }

        ProxyList[arg["name"]] = self


    def grep_proxy_from_db(self):

        if self.setting["ObjectId"]:
            find_req = {
                "anoy": self.setting["anoy"],
                "_id": {
                    "$gt": self.setting["ObjectId"]
                }
            }
        else:
            find_req = {
                "anoy": self.setting["anoy"],
            }

        return self.setting["collection"].find(find_req, {
            "proxy_host": 1,
            "proxy_port": 1,
            "anoy": 1,
            "data_source": 1,
        }).sort([("_id", 1)]).limit(self.setting["cache_size"]).to_list(length=None)


    @tornado.gen.coroutine
    def get_a_proxy(self):

        if not self.setting["proxy_list"]:
            try:
                self.setting["proxy_list"] = yield self.grep_proxy_from_db()
            except:
                logging.my_exc("Find proxy_item from mongodb failed.")
                raise Exception("Find proxy_item from mongodb failed.")

            # come to an end of loop, start form the beginning again
            if len(self.setting["proxy_list"]) != self.setting["cache_size"]:

                logging.info("Warning: obtained %s new available proxies, less than expected %d." % (len(self.setting["proxy_list"]), self.setting["cache_size"]))

                self.setting["ObjectId"] = None
                if not self.setting["proxy_list"]:
                    self.setting["proxy_list"] = yield self.grep_proxy_from_db()

        if not self.setting["proxy_list"]:
            logging.error("No available proxy: proxy_list is empty.")
            raise Exception("No available proxy.")

        raise tornado.gen.Return( self.setting["proxy_list"].pop() )


    @tornado.gen.coroutine
    def disable_a_proxy(self, proxy_item):

        # move to unavailable_pool
        yield [
            self.setting["collection"].remove({"_id": proxy_item["_id"]}),
            self.setting["unavailable_collection"].update({
                "proxy_host": proxy_item["proxy_host"],
                "proxy_port": proxy_item["proxy_port"],
            }, { x:proxy_item[x] for x in proxy_item if x != "_id" }, upsert=True, multi=False)
        ]
