#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import traceback

import tornado.web
import tornado.gen


class TemplateHandler(tornado.web.RequestHandler):

    def initialize(self, root, default_filename=None):
        self.root = os.path.abspath(root) + os.path.sep
        self.default_filename = default_filename

    def _validate_absolute_path(self):
        """
            Do not allow listing directory
            403 do not allow directory dumping
            404 for other cases
        """
        if os.path.isabs(self.path) or ".." in self.path:
            raise tornado.web.HTTPError(403)

        absolute_path = os.path.abspath(os.path.join(self.root, self.path))
        if not absolute_path.startswith(self.root) or not os.path.isfile(absolute_path):
            raise tornado.web.HTTPError(404)

        return absolute_path

    def get(self, path):
        """
            Render request to the file in self.root
        """
        try:
            self.path = path
            self.absolute_path = self._validate_absolute_path()
            self.render(self.absolute_path, data=None, error=None)
        except Exception as e:
            self.set_status(500)
            self.render("error", data=None, error=str(e))


class DefaultRouterHandler(tornado.web.RequestHandler):

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
            request_data["status"] = 404
            request_data["error_msg"] = "404: Not found"
        elif re.match(r"^application/json[;]?(\s*charset=UTF-8)?$", self.request.headers.get("Content-Type"), re.I) is None:
            request_data["status"] = 400
            request_data["error_msg"] = "`Content-Type` Must be `application/json; charset=UTF-8`"
        else:
            try:
                request_data["body"] = json.loads(self.request.body)
            except Exception:
                request_data["status"] = 400
                request_data["error_msg"] = "Request body Must be in `JSON` format"

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
        try:
            request_data, handler = self._validate_post_request()

            if request_data["status"] != 200:
                self._send_response(request_data["status"], request_data["error_msg"])
            else:
                response = yield handler(self, request_data["body"])

        except Exception as e:
            print(traceback.format_exc())
            self._send_response(500, {"data": "", "desc": str(e)})
        else:
            self._send_response(200, {"data": response, "desc": "success"})
