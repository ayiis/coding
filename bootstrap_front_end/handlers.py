#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import traceback
import time

import tornado.web
import tornado.gen


class BaseHandler(tornado.web.RequestHandler):

    system_start_ts = time.time()

    def write_error(self, status_code, **kwargs):
        """
            Common error handler
            If you want to handle error by yourself
        """
        # if status_code != 404 and "exc_info" in kwargs:
        #     print("".join(traceback.format_exception(*kwargs["exc_info"])))
        if not self._finished:
            self.render("error", data=None, error="HTTP %d: %s" % (status_code, self._reason))

    def get_absolute_path(self, root, path):
        """
            Dirty way to fixed a leak on StaticHandler
            Overwrite `get_absolute_path` and `validate_absolute_path`
        """
        return path

    def validate_absolute_path(self, root, path):
        """
            prevent hack
                - 403 directory dumping / absolute path detecting
                - 404 directory listing
        """
        root = os.path.abspath(root) + os.path.sep

        if os.path.isabs(path) or ".." in path:
            raise tornado.web.HTTPError(403, reason=None)

        absolute_path = os.path.abspath(os.path.join(root, path))
        if not absolute_path.startswith(root) or not os.path.isfile(absolute_path):
            raise tornado.web.HTTPError(404, reason=None)

        return absolute_path


# class StaticHandler(tornado.web.StaticFileHandler):
class StaticHandler(BaseHandler, tornado.web.StaticFileHandler):
    pass


class TemplateHandler(BaseHandler):

    def initialize(self, root, default_filename=None):
        self.root = root
        self.default_filename = default_filename

    def get(self, path):
        """
            Render request to the file in self.root
        """
        self.set_secure_cookie("access_code", "whoami", expires=None)
        aaa = self.get_secure_cookie("access_code")
        print("aaa:", aaa)
        self.path = path or self.default_filename
        self.absolute_path = self.validate_absolute_path(self.root, self.path)
        # self.render(self.absolute_path, data=None, error=None)

        print("absolute_path:", self.absolute_path)
        argv = {
            "path": self.absolute_path,
            "data": None,
            "error": None
        }
        self.render("render", argv=argv)
