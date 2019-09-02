import requests
import time
from inspect import getframeinfo, stack
import q
import re
import json
"""
    完全自营的 venderId=0 && shopId=0
"""
["100004571288", "43871571802", "44066755622", "100004571284", "6297458", "883590", "37440870409", "3028550", "2156288", "4311591", "32466384930", "32366918253", "4738339", "45146765595", "45123352721", "44887833654", "1178758", "42907094947", "3176328", "8773619", "7252399", "31894659391", "27026211189", "30944374131", "1480495155", "27800176244", "43287897060", "11151078273", "30520938198", "4508158", "41380832868", "28034401262", "100002040039", "41220108504", "40409428103", "8703798", "6888690", "7102615", "100001648875", "100002219716", "8759446", "100001648715", "4214058", "30892181105", "100001673630", "7038944", "4491749", "6888702", "7102639", "331329", "631418", "331326", "285997", "4491751", "332125", "4279786", "501616"]

MY_AREA = "19_1601_3635_0"
JQNAME = "jQuery8287926"

ITEMID = "43871571802"
CONTENT_URL = "https://item.jd.com/%s.html"
STORE_URL = "https://c0.3.cn/stock?skuId=%s&area=%s&venderId=%s&buyNum=1&choseSuitSkuIds=&cat=%s&extraParam={%%22originid%%22:%%221%%22}&fqsp=0&pdpin=&pduid=%s&ch=1&callback=%s"
PROMOTE_URL = "https://cd.jd.com/promotion/v2?skuId=%s&area=%s&shopId=%s&venderId=%s&cat=%s&isCanUseDQ=1&isCanUseJQ=1&platform=0&orgType=2&jdPrice=%s&appid=1&_=%s&callback=%s"

# 活动凑单页面
GET_PROMOTE_URL = "https://search.jd.com/Search?activity_id=%s"

# 满返页面
MFDETAIL = "https://a.jd.com/mfdetail.html?mfid=%s"

# 可用的券 (登陆后可见)
COUPONS = "https://item.jd.com/coupons?skuId=%s&cat=%s&venderId=%s&isCanUseDQ=isCanUseDQ-1&isCanUseJQ=isCanUseJQ-1"


# DEBUG = True
DEBUG = False

HEADERS = {
    "referer": "https://www.jd.com/",
    "user-agent": "Mozilla/5.0 (manmanbuy; wm jingdong v1.2.1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
}


def aprint(*args):
    caller = getframeinfo(stack()[1][0])
    date_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    caller_string = "%s@%s:" % (caller.filename, caller.lineno)
    return print(date_string, caller_string, *args)


def get_item_neighbor(content_lines, lineno, maxline=30):
    select_line = content_lines[max(lineno - maxline, 0): min(lineno + maxline, len(content_lines))]
    res = {
        "name": None,
        "cat": None,
        "venderId": None,
        "shopId": None,
    }
    for line in select_line:
        if "venderId:" in line:
            res["venderId"] = re.sub(r"""(.*venderId:|,.*$)""", "", line)
        if "shopId:" in line:
            res["shopId"] = re.sub(r"""(.*shopId:'|',.*$)""", "", line)
        if "cat:" in line:
            res["cat"] = re.sub(r"(.*cat: \[|],.*$)", "", line)

    return res


def get_jsonp_json(jsonp):
    store_api_content = re.sub(r"(^" + JQNAME + r"""\(|\)[;]?\w*$)""", "", jsonp)
    return json.loads(store_api_content)


# 获取页面html内容
# if not DEBUG:
#     content_page_url = CONTENT_URL % ITEMID
#     response = requests.get(content_page_url, headers={}, timeout=16)
#     open("content_page.html", "w").write(response.text)
#     item_content = response.text
# item_content = open("content_page.html", "r").read()

# item_content_lines = item_content.split("\n")
# icat = next((i for (i, x) in enumerate(item_content_lines) if "cat: [" in x), "")
# info = get_item_neighbor(item_content_lines, icat)
# aprint(info)

# for line in item_content_lines[:20]:
#     if "<title>" in line:
#         info["name"] = re.sub(r"""(.*<title>|[【].*[】].*</title>.*$)""", "", line)

info = {
    "name": "0",
    "cat": "1,2,3",
    "venderId": "0",
    "shopId": "0",
}

# 获取 商品基本信息 & 价格
store_api_url = STORE_URL % (
    ITEMID,
    MY_AREA,
    info["venderId"],
    info["cat"],
    str(time.time()).replace(".", ""),
    JQNAME,
)
aprint(store_api_url)

if not DEBUG:
    response = requests.get(store_api_url, headers={}, timeout=16)
    aprint("response:", response)
    open("store_api.js", "w").write(response.text)
    store_api_content = response.text
store_api_content = open("store_api.js", "r").read()

store_api_content_json = get_jsonp_json(store_api_content)
aprint(store_api_content_json)

# 取 商家 名称
vender_string = (store_api_content_json["stock"].get("self_D") or store_api_content_json["stock"].get("D") or {}).get("vender") or "自营"

# 取plus的价格（一般更低）或者原价
price = store_api_content_json["stock"]["jdPrice"].get("tpp") or store_api_content_json["stock"]["jdPrice"]["p"]


# 获取价格以及 促销 & 券 & 礼物
promote_api_url = PROMOTE_URL % (
    ITEMID,
    MY_AREA,
    info["venderId"],
    info["shopId"],
    info["cat"].replace(",", "%2C"),
    price,
    str(time.time()).replace(".", ""),
    JQNAME,
)
aprint(promote_api_url)


if not DEBUG:
    response = requests.get(promote_api_url, headers={}, timeout=16)
    open("promote_api.js", "w").write(response.text)
    promote_api_content = response.text
promote_api_content = open("promote_api.js", "r").read()

promote_api_content_json = get_jsonp_json(promote_api_content)
aprint(promote_api_content_json)

# 行间广告
ads_strings = [x["ad"] for x in promote_api_content_json.get("ads", [])]

# 促销活动
promote_strings = map(lambda x: (x["content"], GET_PROMOTE_URL % x["pid"].split("_")[0]), promote_api_content_json["prom"]["pickOneTag"])
promote_strings = list(promote_strings)
aprint(promote_strings)

# 赠品 礼物
gift_strings = []
for tag in promote_api_content_json["prom"]["tags"]:
    if "gifts" in tag:
        gift_string = map(lambda x: (x["nm"], CONTENT_URL % x["sid"]), tag["gifts"])
        gift_string = list(gift_string)
        gift_strings.append((tag["name"], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(tag["d"]))), gift_string))
        aprint(gift_strings[-1])
    elif "name" in tag:
        gift_strings.append((tag["name"], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(tag["d"])))))
        aprint(gift_strings[-1])

# 返券 返点
feedback_strings = ""
if promote_api_content_json.get("quan"):
    feedback_url = promote_api_content_json["quan"]["actUrl"] or (MFDETAIL % promote_api_content_json["quan"]["activityId"])
    if feedback_url[:2] == "//":
        feedback_url = "https:%s" % feedback_url
    feedback_strings = (feedback_url, promote_api_content_json["quan"]["title"])


# 领取优惠券 使用优惠券
quan_strings = []
if promote_api_content_json.get("skuCoupon"):
    for item in promote_api_content_json["skuCoupon"]:
        quan_string = item.get("allDesc") or "满%s减%s" % (item["quota"], item["discount"])
        quan_strings.append(quan_string)

use_info = {
    "id": ITEMID,
    "name": info["name"],
    "price": price,
    "vender": vender_string,
    "venderid": info["venderId"],
    "cat": info["cat"],
    "stock": store_api_content_json["stock"]["StockStateName"],
    "promote": promote_strings,
    "gift": gift_strings,
    "quan": quan_strings,
    "feedback": feedback_strings,
    "ads": ads_strings,
}

aprint(use_info)

