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
CONTENT_URL = "https://goods.kaola.com/product/%s.html"

# 库存 / 价格 / 活动 / 礼物
PROMOTE_URL = "https://goods.kaola.com/product/getPcGoodsDetailDynamic.json?provinceCode=%s&cityCode=%s&districtCode=%s&goodsId=%s&categoryId=%s&t=%s"

# 地址： 广东 / 广州 / 荔湾
MY_AREA = ("440000", "440100", "440103")

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
        open("kaola.base_url_page.html", "w").write(tool.try_decode_html_content(response.body))
    item_content = open("kaola.base_url_page.html", "r").read()
    item_content_lines = item_content.split("\n")
    icat = next((i for (i, x) in enumerate(item_content_lines) if "$addGoods" in x), -1)
    info_text = item_content_lines[icat + 1:icat + 12]

    for i, line in enumerate(info_text):
        if "," in info_text[i]:
            info_text[i] = info_text[i][:info_text[i].index(",")]
            info_text[i] = info_text[i].replace("'", "").strip()
        else:
            ap("[WARN]:", "Something unexpected happened.")
            info_text[i] = ""

    info = {
        "分类id": info_text[0],
        "品牌id": info_text[1],
        "商品名称": info_text[2],
        "itemid": info_text[3],
        "商品售价": info_text[4],
        # "商品图片": info_text[5],
        "分类名": info_text[6],
        "品牌名": info_text[7],
        "商品库存": info_text[8],
        "网络价": info_text[9],
        # "收藏人数": info_text[10],
    }

    return info


@tornado.gen.coroutine
def get_promote_info(info):

    # 获取价格以及 促销 & 券 & 礼物
    promote_api_url = PROMOTE_URL % (
        MY_AREA[0],
        MY_AREA[1],
        MY_AREA[2],
        info["itemid"],
        info["分类id"],
        int(time.time() * 1000),
    )

    # 获取页面html内容
    if not DEBUG:
        response = yield tool.http_request({
            "url": promote_api_url,
            "method": "GET",
            "headers": HEADERS
        })
        open("kaola.promopt_page.html", "w").write(tool.try_decode_html_content(response.body))

    item_content = open("kaola.promopt_page.html", "r").read()
    item_content = tool.json_load(item_content)

    # 这两个不是一模一样的吗
    skuPrice = item_content["data"].get("skuPrice") or item_content["data"]["skuDetailList"][0]["skuPrice"]
    min_price = min(skuPrice["currentPrice"], skuPrice["kaolaPrice"], skuPrice["suggestPrice"], skuPrice["marketPrice"])
    presale = item_content["data"].get("depositGoodsAdditionalInfo") or item_content["data"]["skuDetailList"][0]["depositSkuAdditionalInfo"]
    if presale:
        min_price = presale.get("handPrice") or min_price

    current_store = item_content["data"].get("goodsCurrentStore") or item_content["data"]["skuDetailList"][0]["skuStore"]["currentStore"]

    promotion_info = item_content["data"].get("promotionList") or item_content["data"]["skuDetailList"][0]["promotionList"] or []
    promote = [
        [
            x["promotionContent"],
            x["promotionUrl"],
            "0000 ~ 0000"
        ] for x in promotion_info
    ]

    quan = item_content["data"].get("goodsCouponList") or []

    # q.d()

    return {
        "min_price": min_price,
        "current_store": current_store,
        "promote": promote,
        "quan": quan,
        "presale": bool(presale),
    }


@tornado.gen.coroutine
def test():
    iid = "2544379"
    base_url = get_item_url_by_id(iid)
    info = yield get_base_info({
        "url": base_url
    })

    ap(info)

    promote_info = yield get_promote_info(info)

    ap(promote_info)

    tornado.ioloop.IOLoop.current().stop()
