#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import tornado
import tornado.gen
import re, traceback

from common import tool

POST_URL_RULES = {None: lambda error_msg: error_msg }
GET_URL_RULES = {}


# 添加POST URL对应的处理方法
def add_post_url_handlers(url_handler_obj):
    POST_URL_RULES.update(url_handler_obj)


# 添加GET URL对应的处理方法
def add_get_url_handlers(url_handler_obj):
    GET_URL_RULES.update(url_handler_obj)


class DefaultRouterHandler(tornado.web.RequestHandler):

    # 验证请求的格式，内容
    def validate_post_request(self):
        result = {
            "status": 200,
            "body_json": None,
            "error_msg": None,
        }
        # 请求必须是JSON格式字符串
        if re.match(r"^application/json[;]?(\s*charset=UTF-8)?$", self.request.headers.get("Content-Type"), re.I) is None:
            result["status"] = 400
            result["error_msg"] = "`Content-Type` Must be `application/json; charset=UTF-8`"
        else:
            try:
                result["body_json"] = tool.json_load(self.request.body)
            except:
                result["status"] = 400
                result["error_msg"] = "Request body Must be in `JSON` format"
                return result

        # 请求的URL必须存在
        if POST_URL_RULES.get(self.request.uri) is None:
            result["status"] = 404
            result["error_msg"] = POST_URL_RULES[None]("404: You know what it means")

        return result


    # 验证请求的格式，内容
    def validate_get_request(self):
        result = {
            "status": 200,
            "render_page": None,
            "error_msg": None,
        }
        if GET_URL_RULES.get(self.request.path, None) is None:
            result["status"] = 404
            result["render_page"] = "error.html"
            result["error_msg"] = "404: You know what it means"
        else:
            result["status"] = 200
            result["render_page"] = GET_URL_RULES[self.request.path]
            result["error_msg"] = ""

        return result


    # POST 返回内容
    def send_response(self, status_code, data):
        self.set_status(status_code)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.finish(tool.json_stringify(data))


    def get(self, *args, **kwargs):
        request_data = self.validate_get_request()
        try:
            self.set_status(request_data["status"])
            self.render(request_data["render_page"], selff=self, error=request_data["error_msg"])
        except Exception, e:
            print traceback.format_exc()
            self.set_status(500)
            self.render("error.html", error=str(e))


    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        request_data = self.validate_post_request()
        if request_data["status"] != 200:
            self.send_response(request_data["status"], request_data["error_msg"])
        else:
            try:
                # 获取url对应的处理方法
                handler = POST_URL_RULES.get(self.request.path)
                response = yield handler(self, request_data["body_json"])
            except Exception, e:
                print traceback.format_exc()
                self.send_response(200, { "code": 500, "data": "", "desc": str(e) })
            else:
                self.send_response(200, { "code": 200, "data": response, "desc": "success" })
