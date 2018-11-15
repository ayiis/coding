import json
import datetime
import time
import decimal
import enum


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
        elif isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, Exception):
            return {
                "error": obj.__class__.__name__,
                "args": obj.args,
            }
        else:
            return json.JSONEncoder.default(self, obj)


def wrap_unicode(data):
    if isinstance(data, dict):
        return {wrap_unicode(key): wrap_unicode(value) for key, value in data.iteritems()}
    elif isinstance(data, list):
        return [wrap_unicode(element) for element in data]
    elif isinstance(data, unicode):
        return data.encode("utf-8")
    else:
        return data


def json_stringify(data):
    return json.dumps(wrap_unicode(data), cls=MyEncoder, encoding="utf-8", ensure_ascii=False)


def json_load(data):
    return wrap_unicode(json.loads(data))
