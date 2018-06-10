#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import datetime, time
import re
import traceback
import json
import config

import tornado
from tornado import gen, ioloop, httpclient
from urllib import urlencode
from common import tool, my_tornado_timmer

google_curreny_url = "http://172.18.36.166/my_get_currency_router?a=1&from=%s&to=%s"
# reuters_curreny_url = "https://www.reuters.com/assets/jsonCurrencyConverter?callback=convertCurrency&srcCurr=%s&destCurr=%s"
reuters_curreny_url = "http://172.18.36.166/my_get_currency_router_reuters?srcCurr=%s&destCurr=%s"

currency_result = {}
all_timeout = 15

@gen.coroutine
def crawler_page_end(base_url):
    req_data = {
        "url": reuters_curreny_url % (from_currency, to_currency),
        "method": "GET",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
        },
    }
    response = yield tool.http_request(req_data)
    if response.code == 599:
        response = yield tool.http_request(req_data)

    if response.code != 200:
        raise Exception("http status code %s,%s" % (response.code, response.error))

    html_json_body = json.loads(response.body)
    currency_result[(from_currency, to_currency)] = float(html_json_body["src2Dest"].replace(',', '')) or None
    currency_result[(to_currency, from_currency)] = float(html_json_body["dest2Src"].replace(',', '')) or None


@gen.coroutine
def send_to_wx(req_data):
    # raise gen.Return("")
    request = tornado.httpclient.HTTPRequest(
        url="http://172.18.36.166/.send",
        method="POST",
        headers={
            "username": "ayiis",
        },
        body=urlencode(req_data),
        request_timeout=all_timeout,
        connect_timeout=all_timeout
    )
    response = yield client.fetch(request, raise_error=False)

    print "send_to_wx:", response.body


@gen.coroutine
def do(db):

    db_exchange_rate = db[config.MONGODB["MY_WORLD_STAR_POLICY"]["COLLECTIONS"]["EXCAHANGE_RATES"]]
    operate_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print "%s in auto_refresh_exchange_rate." % operate_datetime

    try:
        result = yield db_exchange_rate.aggregate([{
            "$out": "exchange_rates_bak_%s" % operate_datetime
        }]).to_list(length=None)
    except Exception, e:
        print traceback.format_exc()
        yield send_to_wx({
            "text": "auto_refresh_exchange_rate run FAILED",
            "desp": "exchange_rates $out failed:\r\n```python\r\n%s\r\n```" % (traceback.format_exc())
        })
        raise

    try:
        ts = datetime.datetime.now()
        total_count = 0.0
        sucess_count = 0.0
        error_message_list = []

        currencys = config.CURRENCY["currency_list"].keys()
        for i, currency_from in enumerate(currencys):
            for j, currency_to in enumerate(currencys[i:]):
                print "doing:", currency_from, currency_to
                if currency_from == currency_to:
                    currency_result[(currency_from, currency_to)] = 1.0
                else:
                    total_count += 1
                    currency_result[(currency_from, currency_to)] = None
                    currency_result[(currency_to, currency_from)] = None

                    try:
                        yield get_currency(currency_from, currency_to)
                        sucess_count += 1
                    except Exception, e:
                        print "Exception in get_currency of %s-%s; %s" % (currency_from, currency_to, e)
                        error_message_list.append("Exception in get_currency of %s-%s; %s" % (currency_from, currency_to, e))

        mongo_update_list = []
        for key in currency_result:
            if not currency_result[key]:
                print "None val pass:", key, currency_result[key]
                continue

            mongo_update_list.append(db_exchange_rate.update({
                        "currency_code" : key[0],
                        "exchange_currency_code" : key[1],
                    }, {
                        "$set": {
                            "currency_code" : key[0],
                            "currency_name" : config.CURRENCY["currency_list"][key[0]],
                            "exchange_currency_code" : key[1],
                            "exchange_currency_name" : config.CURRENCY["currency_list"][key[1]],
                            "exchange_rate" : currency_result[key],
                            "operator_code" : "20160105",
                            "operator_name" : "ayiis",
                            "operate_datetime": operate_datetime,
                            "__v" : 0
                    }
                }, multi=True, upsert=True)
            )

        try:
            yield mongo_update_list
        except Exception, e:
            print "Mongo upsert failed: %s" % (e)

        ## send to my wechat

        currency_result_str = {}
        for key in currency_result:
            currency_result_str["%s-%s" % (key[0], key[1])] = currency_result[key]

        duration = round((datetime.datetime.now() - ts).total_seconds(), 2)
        success_rate = round(sucess_count / total_count * 100, 2)
        wx_body = """\r\n```javascript\r\n%s\r\n``` """ % json.dumps(currency_result_str).replace(''', "''', ''',\r\n"''')
        error_message = "\r\n".join(error_message_list)

        yield send_to_wx({
            "text": "Get Currency result",
            "desp": "Success: %s%%; Cost: %ss\r\n\r\nError:\r\n%s\r\n%s\r\n" % (success_rate, duration, error_message, wx_body)
        })
    except Exception, e:
        print traceback.format_exc()
        yield send_to_wx({
            "text": "auto_refresh_exchange_rate run FAILED",
            "desp": "traceback:\r\n```python\r\n%s\r\n```" % (traceback.format_exc())
        })
        raise


@gen.coroutine
def init(db):
    try:
        time_start = int(time.time())
        db_result = yield db.counters.find_and_modify(
            query={"_id": "cronjob_auto_refresh_exchange_rate", "time_start": {"$lt": time_start}},
            update={"$set": {"time_start": time_start + 5}},
            upsert=True
        )
        my_tornado_timmer.set_clock(config.CURRENCY["refresh_clock"], lambda: do(db))

    except Exception, e:
        if e.details["codeName"] == "DuplicateKey":
            print "[INFO] counter 已经存在"
        else:
            print "[ERROR] 数据库连接失败: 汇率定时任务初始化失败"
            print traceback.format_exc()

