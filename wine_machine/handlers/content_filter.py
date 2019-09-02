#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from bson.objectid import ObjectId
from common.mongodb import DBS
from common.tool import aprint as ap
import q
from operator import itemgetter, attrgetter

table_filter = DBS["rent_a_life"]["filter"]


@tornado.gen.coroutine
def filter_fresh_data(collection, website="douban"):
    """
        用 filter 更新指定表 collection 的数据
    """
    content_filter = yield table_filter.find_one({"website": website})

    update_all_data = yield collection.update_many({}, {
        "$set": {
            "skip": 1,
        }
    })

    db_query = {
        "$and": [],
        "$or": [
            {
                "price": 0
            },
            {
                "price": {
                    "$gte": content_filter.get("price_min", 0),
                    "$lte": content_filter.get("price_max", 99999),
                }
            }
        ],
    }

    if content_filter.get("title"):
        """
            .*(?<!(非|不是|不|无))(游戏|娱乐).*
            .*([^非是不无]|^)(游戏|娱乐).*

            https://alf.nu/RegexGolf
            https://www.regextester.com/15

            https://gist.github.com/Davidebyzero/9221685
            https://gist.github.com/jonathanmorley/8058871
        """
        db_query["$and"].append({
            "title": {
                "$not": {
                    # nothing do with to match 非合租
                    # "$regex": "(%s)" % "|".join(content_filter["title"])

                    # lookbehind is not a good idea. https://stackoverflow.com/questions/3796436/whats-the-technical-reason-for-lookbehind-assertion-must-be-fixed-length-in-r
                    # error: lookbehind assertion is not fixed length
                    # "$regex": "^.*(?<!(%s))(%s).*$" % ("|".join(content_filter["not"]), "|".join(content_filter["title"]))

                    # So limit `not` to 1 char
                    # BUG: []不能匹配0个字符，比如 "求租" 无法匹配
                    # "$regex": "^.*[^%s](%s).*$" % ("".join(content_filter["not"]), "|".join(content_filter["title"]))
                    "$regex": ".*([^%s]|^)(%s).*" % ("".join(content_filter["not"]), "|".join(content_filter["title"])),
                    "$options": "i"
                }
            }
        })

    if content_filter.get("author"):
        db_query["$and"].append({
            "author": {
                "$not": {
                    "$regex": "(%s)" % "|".join(content_filter["author"])
                },
                "$nin": content_filter.get("author_full_name", [])
            }
        })

    ap("db_query:", db_query)

    update_all_data = yield collection.update_many(db_query, {
        "$set": {
            "skip": 0
        }
    })

    raise tornado.gen.Return(update_all_data)
