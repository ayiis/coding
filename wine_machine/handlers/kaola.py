#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen
from bson.objectid import ObjectId
from common.mongodb import DBS
from common.tool import aprint as ap
import q
from operator import itemgetter, attrgetter

table_kaola_itemid = DBS["wm"]["kaola_itemid"]
table_kaola_price = DBS["wm"]["kaola_price"]


@tornado.gen.coroutine
def task_add(handler, req_data):
    ap(req_data)

    result = None
    exists_items = yield table_kaola_itemid.find({
        "itemid": {
            "$in": req_data["itemid_list"]
        }
    }).to_list(length=None)

    exists_items = set([x["itemid"] for x in exists_items])
    items = [{"itemid": x, "status": req_data["status"]} for x in (set(req_data["itemid_list"]) - exists_items)]
    result = yield table_kaola_itemid.insert_many(items)
    result = result.inserted_ids

    raise tornado.gen.Return((result, 1))


@tornado.gen.coroutine
def task_list(handler, req_data):
    ap(req_data)
    db_query = {}
    if req_data.get("name"):
        db_query["name"] = {
            "$regex": "^" + "".join(["(?=.*%s)" % s for s in req_data["name"].split(" ") if s.strip()]) + ".*$"
        }
        # db_query["$and"] = [{"name": {"$regex": s}} for s in req_data["name"].split(" ") if s.strip()]

    if req_data.get("status"):
        db_query["status"] = req_data["status"]

    print("db_query:", db_query)
    result = yield table_kaola_itemid.find(db_query).to_list(length=None)
    result_detail = yield table_kaola_price.find({
        "_id": {
            "$in": [x["_id"] for x in result]
        }
    }).sort([("datetime", -1)]).to_list(length=None)

    for item in result:
        item_detail = next((x for x in result_detail if x["_id"] == item["_id"]), {})
        item["price"] = item_detail.get("min_price", 0)
        item["vender"] = "自营"
        item["stock"] = item_detail.get("current_store", 0)
        item["datetime"] = item_detail.get("datetime", "")
        item["quan"] = item_detail.get("quan", "")
        item["promote"] = item_detail.get("promote", "")
        item["presale"] = item_detail.get("presale", "")

    result = sorted(result, key=lambda x: x.get("datetime"), reverse=True)

    raise tornado.gen.Return((result, len(result)))


@tornado.gen.coroutine
def task_update_status(handler, req_data):
    ap(req_data)

    result = yield table_kaola_itemid.update_one({
        "_id": ObjectId(req_data["_id"]),
    }, {
        "$set": {
            "status": int(req_data["status"]),
        }
    })

    raise tornado.gen.Return((result.raw_result, 1))


@tornado.gen.coroutine
def update_good_price(handler, req_data):
    ap(req_data)

    result = yield table_kaola_itemid.update_one({
        "_id": ObjectId(req_data["_id"]),
    }, {
        "$set": {
            "good_price": int(req_data["good_price"]),
        }
    })

    raise tornado.gen.Return((result.raw_result, 1))

