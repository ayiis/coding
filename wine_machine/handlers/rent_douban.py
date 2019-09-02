#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen
from bson.objectid import ObjectId
from common.mongodb import DBS
from common.tool import aprint as ap
import q
from operator import itemgetter, attrgetter
from handlers import content_filter

table_douban = DBS["rent_a_life"]["douban"]
table_filter = DBS["rent_a_life"]["filter"]


@tornado.gen.coroutine
def change_filter(handler, req_data):
    ap(req_data)

    upsert_data = {
        "website": req_data["website"],
    }
    for key in ("title", "author", "author_full_name", "not"):
        if isinstance(req_data[key], list):
            upsert_data[key] = req_data[key]
        else:
            upsert_data[key] = req_data[key].split(",")

    for key in ("price_min", "price_max"):
        upsert_data[key] = req_data[key]

    query_data = {
        "website": req_data["website"],
    }
    result = yield table_filter.update_one(query_data, {"$set": upsert_data}, upsert=True)

    result = yield content_filter.filter_fresh_data(table_douban, "douban")

    raise tornado.gen.Return((result.modified_count, 1))


@tornado.gen.coroutine
def query_filter(handler, req_data):
    ap(req_data)

    db_query = {
        "website": req_data["website"],
    }
    result = yield table_filter.find_one(db_query)
    raise tornado.gen.Return((result, 1))


@tornado.gen.coroutine
def task_list(handler, req_data):

    ap(req_data)
    page_index = req_data.get("page_index", 1) - 1
    page_size = req_data.get("page_size", 50)

    sort_query = {
        "sortby": req_data.get("sortby", "date"),
        "order": req_data.get("order", -1),
    }
    db_query = {"skip": 0}
    if req_data.get("title"):
        db_query["title"] = {
            "$regex": "^" + "".join(["(?=.*%s)" % s for s in req_data["title"].split(" ") if s.strip()]) + ".*$"
        }

    if req_data.get("author"):
        db_query["author"] = req_data["author"]

    if req_data.get("group"):
        db_query["group_name"] = req_data["group"]

    print("db_query:", db_query)

    # db_find = table_douban.find(db_query)
    result_count = yield table_douban.count_documents(db_query)
    result_list = yield table_douban.find(db_query).sort([
        (sort_query["sortby"], sort_query["order"])
    ]).skip(page_index * page_size).limit(page_size).to_list(length=None)

    for item in result_list:
        del item["_id"]

    raise tornado.gen.Return((result_list, result_count))

