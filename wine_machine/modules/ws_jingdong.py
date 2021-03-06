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
from modules import calc_discount

import tornado.gen

table_jingdong_itemid = DBS["wm"]["jingdong_itemid"]
table_jingdong_price = DBS["wm"]["jingdong_price"]
table_jingdong_price_old = DBS["wm"]["jingdong_price_old"]

BASE_NAME = ("name", "cat", "venderId", "shopId")
COMPARE_KEYS = ("price", "stock", "promote", "presale_info")    # gift ads vender good_price feedback # quan单独计算
PROMOTE_FILTER = "换购|即赠"


@tornado.gen.coroutine
def get_base_info(item):

    # 每天更新一次 基本信息
    if "datetime" in item and item["datetime"][:10] >= tool.get_date("today"):

        # 如果已经所有基本信息都有了，跳过这个步骤
        if not any(1 for x in BASE_NAME if x not in item):
            return False

    result = yield fine_jingdong.get_base_info(item)
    result["datetime"] = tool.get_datetime_string()
    return result


@tornado.gen.coroutine
def get_store_info(item):

    result = yield fine_jingdong.get_store_info(item)
    return result


@tornado.gen.coroutine
def get_promote_info(item):

    result = yield fine_jingdong.get_promote_info(item)
    return result


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
        "calc_price": item.get("calc_price"),
        "calc_advice": item.get("calc_advice"),
        "presale_info": item.get("presale_info"),
    }, indent=2, sort_keys=False)


@tornado.gen.coroutine
def execute():

    # 查 item 的： 商品id & 店铺id 之类的基本信息 状态为 1 的商品
    jingdong_itemid_list = yield table_jingdong_itemid.find(
        {"status": 1}, {"status": False},
        # {"itemid": "3596721"}, {"status": False},     # 香满楼牛奶
    ).to_list(length=None)

    for item in jingdong_itemid_list:

        try:

            if not item.get("url"):
                item["url"] = fine_jingdong.get_item_url_by_id(item["itemid"])

            base_info = yield get_base_info(item)
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
        finally:
            yield tornado.gen.sleep(0.1)

    last_wx = None
    # 为没有值的 item 填充默认值
    for item in jingdong_itemid_list:

        ap("Doing:", item["itemid"], item["name"])

        # 如果之前没有查询到 BASE_NAME 的值，填充一个默认值
        item["cat"] = item.get("cat") or "1,2,3"
        item["name"] = item.get("name") or ""
        item["venderId"] = item.get("venderId") or "0"
        item["shopId"] = item.get("shopId") or "0"

        # 查 item 的： 库存 & 价格 & 店铺名称
        try:
            store_info = yield get_store_info(item)
            # print("store_info:", store_info)
            if not store_info:
                continue

            # ap(store_info)
            item.update(store_info)
        except Exception:
            ap(traceback.format_exc())
            yield tornado.gen.sleep(2)
            continue
        finally:
            yield tornado.gen.sleep(0.5)

        # 查 item 的：促销 & 赠品 & 返券 & 活动广告
        try:
            promote_info = yield get_promote_info(item)
            if not promote_info:
                continue

            # ap(promote_info)
            item.update(promote_info)
        except Exception:
            ap(traceback.format_exc())
            yield tornado.gen.sleep(2)
            continue
        finally:
            yield tornado.gen.sleep(0.5)

        if item.get("presale"):
            # 查 预售 价格
            try:
                presale_info = yield fine_jingdong.get_presale_info(item)
                if presale_info:
                    item["presale_info"] = presale_info
                else:
                    item["presale_info"] = None
                # price
            except Exception:
                ap(traceback.format_exc())
                yield tornado.gen.sleep(2)
            finally:
                yield tornado.gen.sleep(0.5)

        # 对比之前的数据，如果有不同，则插入一条信新的记录，并发送信息到微信上
        try:

            old_item = yield table_jingdong_price.find_one({"_id": item["_id"]})

            calc_price_text = ""
            is_good_price = False
            try:
                calc_discount.JDDiscount.calc(item, old_item)
                if 0 < item["calc_price"] < item.get("good_price", 0):
                    is_good_price = True
                calc_price_text = "\r\n预估价：%s，%s\r\n" % (item["calc_price"], item["calc_advice"])
            except Exception:
                ap(traceback.format_exc())

            # 一开始没有价格信息
            if not old_item:
                # dont yield
                item["datetime"] = tool.get_datetime_string()
                yield table_jingdong_price.insert_one(item)

            else:
                # datetime / good_price 不做比较，先赋予一样的值 跳过
                item["datetime"] = old_item["datetime"]
                if "good_price" in item:
                    old_item["good_price"] = item["good_price"]

                # 如果完全一样
                if old_item == item:
                    # [x for x in item if item[x] != old_item[x]]
                    continue

                # 与原来的价格信息不一样
                else:

                    diff_keys = [x for x in COMPARE_KEYS if item.get(x) and item[x] != old_item.get(x)]

                    # 单独处理 quan
                    if "quan" in item:
                        if "quan" in old_item:
                            """
                                如果券过期，就过滤掉
                                如果旧的券只推送1次，在新券里没有，如果券未过期，就需要继承到新券里
                            """
                            new_quan = {}
                            for it in (old_item["quan"] + item["quan"]):

                                # 旧数据 len == 2
                                if len(it) == 2:
                                    continue

                                # 已过期
                                if it[1].split(" ~ ")[-1] < tool.get_date("today"):
                                    continue

                                new_quan[it[2]] = it

                            old_quan_all = {x[2] for x in old_item["quan"] if len(x) > 3}
                            item["quan"] = [new_quan[x] for x in new_quan]
                            if set(new_quan.keys()) != old_quan_all:
                                diff_keys.append("quan")
                            else:
                                # 如果没有其他的 diff_keys，则全部都一样，不需要更新
                                if not diff_keys:
                                    continue
                                else:
                                    pass
                        else:
                            diff_keys.append("quan")

                    item["datetime"] = tool.get_datetime_string()
                    yield table_jingdong_price.update_one({
                        "_id": item["_id"]
                    }, {
                        "$set": item
                    })
                    del old_item["_id"]
                    yield table_jingdong_price_old.insert_one(old_item)

                    """
                        不提醒：

                            - 涨价

                            - 没了：
                                promote
                                gift 没了
                                quan 没了
                                ads 没了

                                feedback 没了（字符串）

                            stock 变成无货

                            - 无视 vender
                    """
                    if "price" in diff_keys:
                        if 0 < float(old_item["price"]) < float(item["price"]) or float(item["price"]) == -1:
                            diff_keys.remove("price")

                    # 如果新的比旧的少，无视
                    # ads 有时候会是 [] 或 [""] 无视
                    for key in ("promote", "gift", "quan", "ads", "feedback"):
                        for line in item[key]:
                            if line and line not in old_item[key]:
                                # 促销如果是 换购 就无视
                                if not (key == "promote" and re.search(PROMOTE_FILTER, line[0])):
                                    break
                        else:
                            if key in diff_keys:
                                diff_keys.remove(key)
                            continue

                    if "stock" in diff_keys:
                        if old_item["stock"] == "无货" and item["stock"] != "无货":
                            pass
                        else:
                            diff_keys.remove("stock")

                    if not diff_keys:
                        continue

                    # 如果计算后的价格+20% 仍然没有达到好价，忽略
                    if (old_item.get("good_price") or 0) * 1.20 < item["calc_price"] or item["calc_price"] < 1.0:
                        continue

                    content = "\r\n".join([
                        "",
                        ",".join(diff_keys),
                        "",
                        "[商品链接](%s) 好价:%s" % (item.get("url"), old_item.get("good_price") or 0),
                        "%s" % (calc_price_text),   # 新增 预估价
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
                    last_wx = tool.send_to_my_wx(
                        (is_good_price and "__" or "") + "京东" + item["name"],
                        content,
                    )

                    # q.d()
                    # yield last_wx
                    # yield tornado.gen.sleep(3)
                    # exit(1)

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
