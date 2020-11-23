#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2020/11/17
import os
import re
import traceback
from aiohttp.web import HTTPException, Response, json_response
from pathlib import Path


class AyHTTPError(HTTPException):
    def __init__(self, status_code, reason):
        self.status_code = status_code
        super(AyHTTPError, self).__init__(reason=reason)


class ApiHandler:
    _url_handlers = {}
    _good_code = 0
    _error_code = 500

    @classmethod
    def add_handlers(cls, url_handler_obj):
        """
            Define the function to handle the request of certain path
        """
        cls._url_handlers.update(url_handler_obj)

    @classmethod
    async def _prepare_request(cls, req):
        """
            Make sure the request body is json
        """
        handler = cls._url_handlers.get(req.path)
        if handler is None:
            raise AyHTTPError(status_code=404, reason="%s Not found" % req.path)

        if re.match(r"^application/json[;]?(\s*charset=UTF-8)?$", req.headers.get("Content-Type", ""), re.I) is None:
            raise AyHTTPError(status_code=400, reason="`Content-Type` Must be `application/json; charset=utf-8`")

        try:
            json_data = await req.json()
        except Exception:
            print(traceback.format_exc())
            raise AyHTTPError(status_code=400, reason="Fail to parse request json.")

        return handler, json_data

    @classmethod
    def _send_response(cls, res_data, status_code=200):
        """
            必须使用 return 而不是 await：object Response can't be used in 'await' expression
        """
        return json_response(res_data, status=status_code)

    @classmethod
    async def do(cls, req):
        """
            1. 确保请求是 json 格式
            2. 执行路由对应的方法，获得结果
            3. 返回 json 格式的结果
        """
        handler, json_data = await cls._prepare_request(req)

        res_data = {
            "code": cls._good_code,
            "data": None,
            "desc": "",
        }

        # 发送到对应的执行者执行
        try:
            data = await handler(json_data)
            res_data.update({
                "data": data,
            })
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            res_data.update({
                "code": cls._error_code,
                "desc": str(e),
            })

        # 返回 json 结果
        # 必须 return 到外层
        try:
            return cls._send_response(res_data)
        except Exception as e:
            print("Response error: %s" % (e), flush=True)


class TemplateHandler:
    """
        1. 直接将 build 好的 html 缓存在内存中
        2. 当访问的路径 + jade 可以匹配时，返回内存中的内容
        3. 简单粗暴高效，适合小型网站
        4. 模板的所有修改，重启后才能生效
        5. 其实就没有用到生成的 src 的文件了，src 只能方便参考
    """

    @classmethod
    def wrap(cls, templete_path, templete, index="index"):

        cls.templete_path = os.path.abspath(os.path.join(os.path.abspath("."), templete_path))
        cls.templete = templete

        def do(req):

            req_path = req.path

            if req_path == "/":
                req_path = "/%s" % (index)

            target_path = os.path.abspath("%s/%s.jade" % (cls.templete_path, req_path))
            if not(target_path in cls.templete and target_path.startswith(cls.templete_path) and os.path.isfile(target_path)):
                raise AyHTTPError(status_code=404, reason="%s Not found" % req_path)

            return Response(
                body=cls.templete[target_path],
                status=200,
                content_type="text/html",
                charset="utf8",
            )

        return do
