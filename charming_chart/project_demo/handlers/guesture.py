#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import q
import tornado.web
import tornado.gen
from common.mongodb import DBS


@tornado.gen.coroutine
def do_return_ok(handler, req_data):
    req_data["answer"] = "by server"
    raise tornado.gen.Return({"receive": req_data, "ok": True})


@tornado.gen.coroutine
def do_return_sequence_name(handler, req_data):
    sequence_name = yield DBS["db_gestureapi"].get_next_sequence("sequence_counters")
    raise tornado.gen.Return({"sequence_name": sequence_name})


@tornado.gen.coroutine
def do_return_error(handler, req_data):
    assert "key" in req_data, "You are not qualified"
    raise tornado.gen.Return({"pass": True})


@tornado.gen.coroutine
def weekly_summary(handler, req_data):
    # start_date = req_data.get("start_date", "2020-01-01")
    # end_date = req_data.get("end_date", "2020-12-31")
    # sequence_name = yield DBS["db_gestureapi"].get_next_sequence("sequence_counters")
    # print("sequence_name:", sequence_name)
    # db_result = yield DBS["db_gestureapi"]["log_%s" % "2020-05-31"].aggregate([{
    #     "$group": {
    #         "_id": {
    #             "$substr": ["$request_time", 0, 2],
    #         },
    #         "c": {
    #             "$sum": 1
    #         }
    #     }
    # }]).to_list(length=None)

    db_result = {"_id" : "16", "c" : 286.0 }, {"_id" : "13", "c" : 682.0 }, {"_id" : "23", "c" : 56.0 }, {"_id" : "10", "c" : 435.0 }, {"_id" : "17", "c" : 371.0 }, {"_id" : "08", "c" : 240.0 }, {"_id" : "07", "c" : 219.0 }, {"_id" : "11", "c" : 728.0 }, {"_id" : "14", "c" : 406.0 }, {"_id" : "21", "c" : 641.0 }, {"_id" : "09", "c" : 423.0 }, {"_id" : "06", "c" : 112.0 }, {"_id" : "19", "c" : 602.0 }, {"_id" : "20", "c" : 761.0 }, {"_id" : "18", "c" : 316.0 }, {"_id" : "22", "c" : 290.0 }, {"_id" : "15", "c" : 269.0 }, {"_id" : "12", "c" : 365.0 }
    result_data = [0] * 24
    for item in db_result:
        result_data[int(item["_id"])] = item["c"]

    return result_data








