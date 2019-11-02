import time
import q
import re
import json
from common import tool
from common.mongodb import DBS
from common.tool import aprint as ap
from conf import config
import traceback
from modules.fine import kaola as fine_kaola

import tornado.gen

table_kaola_itemid = DBS["wm"]["kaola_itemid"]
table_kaola_price = DBS["wm"]["kaola_price"]
table_kaola_price_old = DBS["wm"]["kaola_price_old"]

BASE_NAME = ("分类id", "itemid")
COMPARE_KEYS = ("min_price", "promote", "quan", "current_store")


@tornado.gen.coroutine
def get_base_info(item):

    # 如果已经所有基本信息都有了，跳过这个步骤
    if not any(1 for x in BASE_NAME if x not in item):
        return False

    result = yield fine_kaola.get_base_info(item)
    return result


@tornado.gen.coroutine
def get_promote_info(item):

    result = yield fine_kaola.get_promote_info(item)
    return result


def get_wx_content(item):
    return tool.json_stringify({
        "商品名称": item["商品名称"],
        "min_price": item["min_price"],
        "current_store": item["current_store"],
        "promote": item["promote"],
        "quan": item["quan"],
    }, indent=2, sort_keys=False)


@tornado.gen.coroutine
def execute():

    # 查 item 的： 商品id & 店铺id 之类的基本信息 状态为 1 的商品
    kaola_itemid_list = yield table_kaola_itemid.find(
        {"status": 1}, {"status": False}
        # {"status": 1, "itemid": "5142333"}, {"status": False}
    ).to_list(length=None)

    ap(kaola_itemid_list)

    for item in kaola_itemid_list:

        try:

            if not item.get("url"):
                item["url"] = fine_kaola.get_item_url_by_id(item["itemid"])

            base_info = yield get_base_info(item)
            if not base_info:
                continue

            item.update(base_info)
            yield table_kaola_itemid.update_one(
                {
                    "_id": item["_id"]
                }, {
                    "$set": base_info
                }
            )
        except Exception:
            ap(traceback.format_exc())
        finally:
            yield tornado.gen.sleep(0.2)

    last_wx = None
    # 为没有值的 item 填充默认值
    for item in kaola_itemid_list:

        ap("Doing:", item["itemid"], item["商品名称"])

        # 如果之前没有查询到 BASE_NAME 的值，填充一个默认值
        item["分类id"] = item.get("分类id") or "0"

        # 查 item 的： 库存 & 价格 & 活动 & 礼物
        try:
            promote_info = yield get_promote_info(item)
            if not promote_info:
                continue

            # ap(promote_info)
            item.update(promote_info)
        except Exception:
            ap(traceback.format_exc())
            continue
        finally:
            yield tornado.gen.sleep(0.2)

        # 对比之前的数据，如果有不同，则插入一条信新的记录，并发送信息到微信上
        try:

            old_item = yield table_kaola_price.find_one({"_id": item["_id"]})

            # 一开始没有价格信息
            if not old_item:
                # dont yield
                item["datetime"] = tool.get_datetime_string()
                yield table_kaola_price.insert_one(item)

            else:
                # datetime 不做比较，先赋予一样的值 跳过
                item["datetime"] = old_item["datetime"]

                # 如果完全一样
                if old_item == item:
                    # [x for x in item if item[x] != old_item[x]]
                    continue

                # 与原来的价格信息不一样
                else:

                    # diff_keys = [x for x in COMPARE_KEYS if item[x] != old_item[x]]
                    diff_keys = [x for x in COMPARE_KEYS if item.get(x) and item[x] != old_item.get(x)]

                    item["datetime"] = tool.get_datetime_string()
                    yield table_kaola_price.update_one({
                        "_id": item["_id"]
                    }, {
                        "$set": item
                    })
                    del old_item["_id"]
                    yield table_kaola_price_old.insert_one(old_item)

                    """
                        不提醒：

                            - 涨价
                            - 变成无货

                    """
                    if "min_price" in diff_keys:
                        if 0 < float(old_item["min_price"]) < float(item["min_price"]) or float(item["min_price"]) == -1:
                            diff_keys.remove("min_price")

                    # 如果新的比旧的少，无视
                    for key in ("quan", ):
                        for line in item[key]:
                            if line and line not in old_item[key]:
                                break
                        else:
                            if key in diff_keys:
                                diff_keys.remove(key)
                            continue

                    if "current_store" in diff_keys:
                        if old_item["current_store"] == "0" and item["current_store"] != "0":
                            pass
                        else:
                            diff_keys.remove("current_store")

                    if not diff_keys:
                        continue

                    content = "\r\n".join([
                        "",
                        ",".join(diff_keys),
                        "",
                        "[新数据](%s)" % (item.get("url")),
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
                    last_wx = tool.send_to_my_wx("考拉" + item["商品名称"], content)

        except Exception:
            ap(traceback.format_exc())
            yield tornado.gen.sleep(2)
        finally:
            yield tornado.gen.sleep(0.5)

    if last_wx:
        try:
            yield last_wx
        except Exception:
            ap(traceback.format_exc())
            ap("Last wx send fail!")


if __name__ == "__main__":
    execute()
