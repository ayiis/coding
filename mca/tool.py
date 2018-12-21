#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import datetime
import re
import time
import decimal
import hashlib
import base64
import traceback
import zlib


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj == datetime.datetime.min:
                return None
            else:
                return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            if obj == datetime.date.min:
                return None
            else:
                return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.timedelta):
            return time.strftime("%H:%M:%S", time.localtime(obj.seconds + 60 * 60 * (24 - 8))) # hacked
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Exception):
            return {
                "error": obj.__class__.__name__,
                "args": obj.args,
            }
        else:
            return json.JSONEncoder.default(self, obj)


def wrap_unicode(data):
    if isinstance(data, dict):
        return {wrap_unicode(key): wrap_unicode(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [wrap_unicode(element) for element in data]
    elif isinstance(data, unicode):
        return data.encode("utf-8")
    else:
        return data


def json_stringify(data):
    return json.dumps(data, cls=MyEncoder, ensure_ascii=False)


def json_load(data):
    return json.loads(data)
