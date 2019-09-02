#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen
from common.mongodb import DBS
from common.tool import aprint as ap
import q

table_jingdong_itemid = DBS["wm"]["jingdong_itemid"]
table_jingdong_price = DBS["wm"]["jingdong_price"]


@tornado.gen.coroutine
def add(handler, req_data):
    ap(req_data)

    result = None
    if req_data.get("site") == "jingdong":
        exists_items = yield table_jingdong_itemid.find({
            "itemid": {
                "$in": req_data["itemid_list"]
            }
        }).to_list(length=None)

        exists_items = set([x["itemid"] for x in exists_items])
        items = [{"itemid": x} for x in (set(req_data["itemid_list"]) - exists_items)]
        if items:
            result = yield table_jingdong_itemid.insert_many(items)
            result = result.inserted_ids

    raise tornado.gen.Return(result)
