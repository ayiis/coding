#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import traceback

import tornado.web
import tornado.gen


class BaseHandler(tornado.web.RequestHandler):

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
        self.path = path or self.default_filename
        self.absolute_path = self.validate_absolute_path(self.root, self.path)
        self.render(self.absolute_path, data=None, error=None)


class ApiHandler(BaseHandler):

    _url_handlers = {}

    @classmethod
    def update_url_handlers(cls, url_handler_obj):
        """
            Define the function to handle the request of certain path
        """
        cls._url_handlers.update(url_handler_obj)

    def _validate_post_request(self):
        """
            convert the request body to json
        """
        request_data = {
            "status": 200,
            "body": None,
            "error_msg": None,
        }

        handler = self._url_handlers.get(self.request.path)
        if handler is None:
            raise tornado.web.HTTPError(404, reason=None)
        elif re.match(r"^application/json[;]?(\s*charset=UTF-8)?$", self.request.headers.get("Content-Type", ""), re.I) is None:
            raise tornado.web.HTTPError(400, reason="`Content-Type` Must be `application/json; charset=UTF-8`")
        else:
            try:
                request_data["body"] = json.loads(self.request.body)
            except Exception:
                print(traceback.format_exc())
                raise tornado.web.HTTPError(400, reason="request json format invalid")

        return request_data, handler

    def _send_response(self, status_code, data):
        """
            write result to the client
        """
        self.set_status(status_code)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.finish(json.dumps(data))

    @tornado.gen.coroutine
    def post(self):
        """
            handle the request, return a json string
        """
        request_data, handler = self._validate_post_request()
        try:
            data = yield handler(self, request_data["body"])
            self._send_response(200, {"data": data, "code": 200, "desc": "success"})
        except Exception as e:
            print(traceback.format_exc())
            self._send_response(200, {"data": None, "code": 500, "desc": str(e)})
