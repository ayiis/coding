import time
import q
import re
import json
from common import tool
from common.mongodb import DBS
from common.tool import aprint as ap
from conf import config
import traceback
from modules.fine import yanxuan as fine_yanxuan

import tornado.gen

table_yanxuan_itemid = DBS["wm"]["yanxuan_itemid"]
table_yanxuan_price = DBS["wm"]["yanxuan_price"]
table_yanxuan_price_old = DBS["wm"]["yanxuan_price_old"]

COMPARE_KEYS = ("promote", "quan", "price")


@tornado.gen.coroutine
def get_base_info(item):
    """
        所有信息都在页面的html上
    """
    result = yield fine_yanxuan.get_base_info(item)
    return result


def get_wx_content(item):
    return tool.json_stringify({
        "name": item["name"],
        "promote": item["promote"],
        "quan": item["quan"],
        "price": item["price"],
        "store": item["store"],
    }, indent=2, sort_keys=False)


@tornado.gen.coroutine
def execute():

    # yield fine_yanxuan.test()
    # exit(1)

    # 查 item 的： 商品id & 店铺id 之类的基本信息 状态为 1 的商品
    yanxuan_itemid_list = yield table_yanxuan_itemid.find(
        {"status": 1}, {"status": False}
        # {"status": 1, "itemid": "5142333"}, {"status": False}
    ).to_list(length=None)

    ap(yanxuan_itemid_list)

    last_wx = None
    for item in yanxuan_itemid_list:

        if not item.get("url"):
            item["url"] = fine_yanxuan.get_item_url_by_id(item["itemid"])

        # 查 item 的： 库存 & 价格 & 活动 & 券
        try:
            base_info = yield get_base_info(item)
            if not base_info:
                continue

            ap(base_info)
            item.update(base_info)
            del base_info["promote"]
            del base_info["quan"]
            yield table_yanxuan_itemid.update_one(
                {
                    "_id": item["_id"]
                }, {
                    "$set": base_info
                }
            )
        except Exception:
            ap(traceback.format_exc())
            continue
        finally:
            yield tornado.gen.sleep(0.2)

        # 对比之前的数据，如果有不同，则插入一条信新的记录，并发送信息到微信上
        try:

            old_item = yield table_yanxuan_price.find_one({"_id": item["_id"]})

            # 一开始没有价格信息
            if not old_item:
                # dont yield
                item["datetime"] = tool.get_datetime_string()
                yield table_yanxuan_price.insert_one(item)

            else:
                # datetime 不做比较，先赋予一样的值 跳过
                item["datetime"] = old_item["datetime"]

                # 如果完全一样
                if old_item == item:
                    # [x for x in item if item[x] != old_item[x]]
                    continue

                # 与原来的价格信息不一样
                else:

                    diff_keys = [x for x in COMPARE_KEYS if item.get(x) and item[x] != old_item.get(x)]

                    item["datetime"] = tool.get_datetime_string()
                    yield table_yanxuan_price.update_one({
                        "_id": item["_id"]
                    }, {
                        "$set": item
                    })
                    del old_item["_id"]
                    yield table_yanxuan_price_old.insert_one(old_item)

                    """
                        不提醒：

                            - 涨价
                            - 变成无货

                    """
                    # 如果新的比旧的少，无视
                    for key in ("quan", "promote"):
                        for line in item[key]:
                            if line and line not in old_item[key]:
                                break
                        else:
                            if key in diff_keys:
                                diff_keys.remove(key)
                            continue

                    if not diff_keys:
                        continue

                    q.d()

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
                    last_wx = tool.send_to_my_wx("严选" + item["name"], content)

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
    # {"status": 1, "itemid": "3441177", "index": 2}
    execute()
