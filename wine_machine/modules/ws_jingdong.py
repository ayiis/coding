import time
import q
import re
import json
from common import tool
from common.mongodb import DBS
from common.tool import aprint as ap
from conf import config
import traceback
from modules.fine import jingdong as fine_jingdong

import tornado.gen

table_jingdong_itemid = DBS["wm"]["jingdong_itemid"]
table_jingdong_price = DBS["wm"]["jingdong_price"]
table_jingdong_price_old = DBS["wm"]["jingdong_price_old"]
base_name = ("name", "cat", "venderId", "shopId")


def get_base_info(item):

    # 如果已经所有基本信息都有了，跳过这个步骤
    if not any(1 for x in base_name if x not in item):
        return False

    return fine_jingdong.get_base_info(item["itemid"])


def get_store_info(item):

    return fine_jingdong.get_store_info(item)


def get_promote_info(item):

    return fine_jingdong.get_promote_info(item)


def get_wx_content(item):
    return tool.json_stringify({
        "name": item["name"],
        "price": item["price"],
        "vender": item["vender"],
        "stock": item["stock"],
        "promote": item["promote"],
        "gift": item["gift"],
        "quan": item["quan"],
        "feedback": item["feedback"],
        "ads": item["ads"],
    }, indent=2, sort_keys=False)


@tornado.gen.coroutine
def execute():

    # 查 item 的： 商品id & 店铺id 之类的基本信息 状态为 1 的商品
    jingdong_itemid_list = yield table_jingdong_itemid.find(
        {"status": 1}, {"status": False}
    ).to_list(length=None)

    for item in jingdong_itemid_list:
        try:
            base_info = get_base_info(item)
            if not base_info:
                continue

            item.update(base_info)
            yield table_jingdong_itemid.update_one(
                {
                    "_id": item["_id"]
                }, {
                    "$set": base_info
                }
            )
        except Exception:
            ap(traceback.format_exc())

    last_wx = None
    # 为没有值的 item 填充默认值
    for item in jingdong_itemid_list:

        # 如果之前没有查询到 base_name 的值，填充一个默认值
        item["cat"] = item.get("cat", "1,2,3")
        item["name"] = item.get("name", "")
        item["venderId"] = item.get("venderId", "0")
        item["shopId"] = item.get("shopId", "0")

        # 查 item 的： 库存 & 价格 & 店铺名称
        try:
            store_info = get_store_info(item)
            if not store_info:
                continue

            ap(store_info)
            item.update(store_info)
        except Exception:
            ap(traceback.format_exc())
            continue

        # 查 item 的：促销 & 赠品 & 返券 & 活动广告
        try:
            promote_info = get_promote_info(item)
            if not promote_info:
                continue

            ap(promote_info)
            item.update(promote_info)
        except Exception:
            ap(traceback.format_exc())
            continue

        # 对比之前的数据，如果有不同，则插入一条信新的记录，并发送信息到微信上
        try:

            old_item = yield table_jingdong_price.find_one({"_id": item["_id"]})

            # 一开始没有价格信息
            if not old_item:
                # dont yield
                item["datetime"] = tool.get_datetime_string()
                yield table_jingdong_price.insert_one(item)

            else:
                # datetime 不做比较，先赋予一样的值 跳过
                item["datetime"] = old_item["datetime"]

                # 如果完全一样
                if old_item == item:
                    # [x for x in item if item[x] != old_item[x]]
                    continue

                # 与原来的价格信息不一样
                else:

                    diff_keys = [x for x in item if item[x] != old_item[x]]

                    item["datetime"] = tool.get_datetime_string()
                    yield table_jingdong_price.update_one({
                        "_id": item["_id"]
                    }, {
                        "$set": item
                    })
                    del old_item["_id"]
                    yield table_jingdong_price_old.insert_one(old_item)
                    content = "\r\n".join([
                        "",
                        ",".join(diff_keys),
                        "",
                        "# 新数据",
                        "",
                        "```json",
                        "%s",
                        "```",
                        "",
                        "# 旧数据",
                        "",
                        "```json",
                        "%s",
                        "```",
                        "",
                    ]) % (get_wx_content(item), get_wx_content(old_item))
                    last_wx = tool.send_to_my_wx(item["name"], content)

                    # q.d()
                    # yield last_wx
                    # yield tornado.gen.sleep(3)
                    # exit(1)

        except Exception:
            ap(traceback.format_exc())
            yield tornado.gen.sleep(2)

        yield tornado.gen.sleep(0.1)

    if last_wx:
        try:
            yield last_wx
        except Exception:
            ap(traceback.format_exc())
            ap("Last wx send fail!")


if __name__ == "__main__":
    execute()
