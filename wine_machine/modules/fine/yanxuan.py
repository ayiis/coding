import time
import q
import re
import traceback
import json
from common import tool, mongodb
from common.tool import aprint as ap
import tornado.gen
"""

"""

# 基本页面
CONTENT_URL = "https://you.163.com/item/detail?id=%s"

# DEBUG = True
DEBUG = False

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
}


def get_item_url_by_id(itemid):
    return CONTENT_URL % itemid


@tornado.gen.coroutine
def get_base_info(item):

    # 获取页面html内容
    if not DEBUG:
        response = yield tool.http_request({
            "url": item["url"],
            "method": "GET",
            "headers": HEADERS
        })
        open("yanxuan.base_url_page.html", "w").write(tool.try_decode_html_content(response.body))

    item_content = open("yanxuan.base_url_page.html", "r").read()
    item_content_lines = item_content.split("\n")
    icat = next((i for (i, x) in enumerate(item_content_lines) if "\"item\":" in x), -1)
    info_text = item_content_lines[icat][7:-1]
    info_json = tool.json_load(info_text)
    # info_text = info_text.replace("\"item\":", "")
    # if info_text[-1] == ",":
    #     info_text = info_text[0:-1]

    if item.get("iid"):
        item_info = next((x for x in info_json["skuList"] if x["id"] == item["iid"]), {})
    else:
        item_info = info_json["skuList"][item["index"]]

    if not item_info:
        return None

    promote_info = item_info.get("hdrkDetailVOList")
    if item_info.get("couponShortNameList"):
        quan_info = item_info.get("couponShortNameList")
    elif item_info.get("shortCouponList"):
        quan_info = [x["displayName"] for x in item_info["shortCouponList"]]
    else:
        quan_info = None

    price = min(item_info["retailPrice"], item_info["counterPrice"], item_info["calcPrice"], item_info["preSellPrice"])

    if item_info.get("spmcBanner"):
        spmc_price = float(item_info["spmcBanner"].get("spmcPrice") or 0)
        price = spmc_price > 0 and min(spmc_price, price) or price

    if item_info.get("detailPromBanner"):
        activity_price = float(item_info["detailPromBanner"].get("activityPrice") or 0)
        price = activity_price > 0 and min(activity_price, price) or price

    info = {
        "name": item_info["skuTitle"],
        "iid": item_info["id"],
        "promote": [[x["name"], x["huodongUrlPc"], "0 ~ 0"] for x in promote_info],
        "quan": quan_info,
        "price": price,
        "store": item_info["sellVolume"],
    }

    return info


@tornado.gen.coroutine
def test():
    iid = "3441177"
    base_url = get_item_url_by_id(iid)
    info = yield get_base_info({
        "url": base_url,
        "index": 2,
    })

    ap(info)

    tornado.ioloop.IOLoop.current().stop()
