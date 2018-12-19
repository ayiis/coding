#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    from mock_data import `shopping_data`
    when POST to shopping, return `shopping_data`
"""
import tornado
import re
from routes.common import tool
import datetime
from tornado import gen
import traceback

URL_RULES = {
    None: lambda error_msg: error_msg,
}


# 添加URL对应的处理方法
def add_url_handler(url, handler):
    URL_RULES[url] = handler


# 验证请求的格式，内容
def validate_request(request):

    result = {
        'status': 200,
        'request_body_json': None,
        'error_msg': None,
    }

    # 请求必须是JSON格式字符串
    if re.match(r'^application/json[;]?(\s*charset=UTF-8)?$', request.headers['Content-Type'], re.I) is None:
        result['status'] = 400
        result['error_msg'] = '`Content-Type` Must be `application/json; charset=UTF-8`'
    else:
        try:
            result['request_body_json'] = tool.json_load(request.body)
        except Exception:
            result['status'] = 400
            result['error_msg'] = 'Request body Must be in `JSON` format'

    # 请求的URL必须存在
    if URL_RULES.get(request.uri) is None:
        result['status'] = 404
        result['error_msg'] = URL_RULES[None]('404: You know what it means')

    return result


class DefaultRouterHandler(tornado.web.RequestHandler):
    def send_response(self, status_code, data):
        self.set_status(status_code)
        self.write(data)    # 返回一个对象时，tornado自动设置application/json，并返回json字符串
        self.finish()

        data = {
            'url': self.request.uri,
            'request_ip': self.request.remote_ip,
            'request': self.request.body,
            'request_raw': str(self.request),       # only for debug
            'code': status_code,
            'response': data,
            'duration': (datetime.datetime.now() - self.ts).total_seconds()
        }
        if hasattr(self, 'error_msg'):
            data['error_msg'] = str(self.error_msg)
        else:
            data['error_msg'] = None

        tool.save_log_to_file(tool.json_stringify(data))

    # not allow `GET`
    def get(self, *args, **kwargs):
        self.ts = datetime.datetime.now()
        self.send_response(405, "Do not allow `GET`")

    # always use `POST`
    @gen.coroutine
    def post(self, *args, **kwargs):
        self.ts = datetime.datetime.now()

        result = validate_request(self.request)
        # 验证失败
        if result['status'] != 200:
            self.send_response(result['status'], result['error_msg'])
            return

        # 获取url对应的处理方法
        handler = URL_RULES.get(self.request.uri)

        try:
            response = yield handler(result['request_body_json'])
        except Exception:
            self.error_msg = traceback.format_exc()
            self.send_response(500, 'Server cause a 500 Error, please contact system admin')
            return

        # if type(response) != str:
        #     response = tool.json_stringify(response)

        self.send_response(200, response)


@gen.coroutine
def future_return(req_data, res_data):
    raise gen.Return(res_data.ret_data)


def init_mock():
    from mock_data import shopping, pricing_by_trips, rule, booking, ticketing, order_query, reissue, refund
    mock_datas = {
        "shopping": shopping,
        "pricing_by_trips": pricing_by_trips,
        "rule": rule,
        "booking": booking,
        "ticketing": ticketing,
        "order_query": order_query,
        "reissue": reissue,
        "refund": refund
    }
    mock_handlers = {}
    for item in mock_datas:
        mock_handlers[item] = lambda req_data, res_data=mock_datas[item]: future_return(req_data, res_data)

    add_url_handler("/air/v2/shopping/i", mock_handlers["shopping"])
    add_url_handler("/air/v2/pricing_by_trips/i", mock_handlers["pricing_by_trips"])
    add_url_handler("/air/v2/rule/i", mock_handlers["rule"])
    add_url_handler("/air/v2/booking/i", mock_handlers["booking"])
    add_url_handler("/air/v2/ticketing/i", mock_handlers["ticketing"])
    add_url_handler("/air/v2/order_query/i", mock_handlers["order_query"])
    add_url_handler("/air/v2/reissue/i", mock_handlers["reissue"])
    add_url_handler("/air/v2/refund/i", mock_handlers["refund"])
