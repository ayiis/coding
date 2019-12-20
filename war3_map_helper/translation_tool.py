"""
    翻译接口:
        1. 百度.计费接口

    可互译语言：
        en 英语
        ru 俄语
        zh 汉语
        swe 瑞典语

        * 已禁用自动检测
"""
import q
import re
import requests
import hashlib
import uuid
import os
import json
import time

from pathlib import Path


def get_md5_digest(text):
    text = text.encode("utf8")
    return hashlib.md5(text).digest().hex()


class BaseFanyi(object):

    def __init__(self, from_lan, to_lan):
        super(BaseFanyi, self).__init__()
        self.cache_path = "./data/dict_base.%s-%s.log" % (from_lan, to_lan)
        self.cache = {}
        self.read_dict_cache()

    def translate(self, text, from_lan=None, to_lan=None):

        if not text:
            return ""

        cache_key = text
        if cache_key in self.cache:
            return self.cache[cache_key]

        self.cache[cache_key] = "((.))"

        return self.cache[cache_key]

    def read_dict_cache(self):
        if Path(self.cache_path).is_file():
            with open(self.cache_path, "r") as rf:
                for lineno, line in enumerate(rf):
                    line = line.strip()
                    if not line:
                        continue
                    key, value = line.split("\0")
                    self.cache[key.lower()] = value

    def save_result(self):
        """
            保存翻译接口的结果
        """
        with open(self.cache_path, "w") as wf:
            for key in self.cache:
                wf.write("%s\0%s%s" % (key, self.cache[key], os.linesep))


class BaiduFanyi(BaseFanyi):
    """
        百度翻译api
    """
    API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def __init__(self, from_lan, to_lan):
        super(BaiduFanyi, self).__init__(from_lan, to_lan)
        self.from_lan = from_lan
        self.to_lan = to_lan
        self.sess = requests.Session()
        self.ts = None
        self.cool_down_time = 1.10
        self.cache = {}
        self.cache_path = "./data/dict_baidu.%s-%s.log" % (from_lan, to_lan)
        self.read_dict_cache()

    def call_baidu_api(self, text):
        random_str = uuid.uuid4().hex
        req_data = {
            "q": text,          # TEXT    Y   请求翻译query   UTF-8编码
            "from": self.from_lan,       # TEXT    Y   翻译源语言   语言列表(可设置为auto)
            "to": self.to_lan,         # TEXT    Y   译文语言    语言列表(不可设置为auto)
            "appid": os.environ["bd_app_id"],      # TEXT    Y   APP ID  可在管理控制台查看
            "salt": random_str,       # TEXT    Y   随机数
            "sign": None,       # TEXT    Y   签名  appid+q+salt+密钥 的MD5值
        }
        req_data["sign"] = get_md5_digest(req_data["appid"] + req_data["q"] + req_data["salt"] + os.environ["bd_app_key"])
        print(req_data)
        res = self.sess.post(BaiduFanyi.API_URL, data=req_data, headers={
            "content-type": "application/x-www-form-urlencoded",
        })
        print(res.text)

        res_json = json.loads(res.text)

        return "\n".join([x["dst"] for x in res_json["trans_result"]])

    def translate(self, text):
        """
            接口限制请求频率为1秒1次，在这里使用 self.ts 计时并限制
            按接口返回结果的那一刻开始重置计时器
        """
        if not text:
            return ""

        # 纯 特殊符号和数字 组成的字符串直接返回
        if re.match(r"^[0-9|\s\+\-\%\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?]+$", text, re.I):
            return text

        # cache_key = "%s-%s\t%s" % (self.from_lan, self.to_lan, text)
        cache_key = text  # .replace("\r", "\1").replace("\n", "\2")
        if cache_key in self.cache:
            return self.cache[cache_key]

        if self.ts:
            cool_down = time.time() - self.ts
            if cool_down < self.cool_down_time:
                time.sleep(self.cool_down_time - cool_down)

        self.cache[cache_key] = self.call_baidu_api(text)  # .replace("\r", "\1").replace("\n", "\2")
        self.ts = time.time()
        return self.cache[cache_key]


class GoogleFanyi(BaseFanyi):
    """
        谷歌翻译
    """
    API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def __init__(self, from_lan, to_lan):
        super(GoogleFanyi, self).__init__(from_lan, to_lan)
        self.from_lan = from_lan
        self.to_lan = to_lan
        self.sess = requests.Session()
        self.ts = None
        self.cool_down_time = 1.10
        self.cache = {}
        self.cache_path = "./data/dict_baidu.%s-%s.log" % (from_lan, to_lan)
        self.read_dict_cache()

    def call_baidu_api(self, text):
        random_str = uuid.uuid4().hex
        req_data = {
            "q": text,          # TEXT    Y   请求翻译query   UTF-8编码
            "from": self.from_lan,       # TEXT    Y   翻译源语言   语言列表(可设置为auto)
            "to": self.to_lan,         # TEXT    Y   译文语言    语言列表(不可设置为auto)
            "appid": os.environ["bd_app_id"],      # TEXT    Y   APP ID  可在管理控制台查看
            "salt": random_str,       # TEXT    Y   随机数
            "sign": None,       # TEXT    Y   签名  appid+q+salt+密钥 的MD5值
        }
        req_data["sign"] = get_md5_digest(req_data["appid"] + req_data["q"] + req_data["salt"] + os.environ["bd_app_key"])
        print(req_data)
        res = self.sess.post(BaiduFanyi.API_URL, data=req_data, headers={
            "content-type": "application/x-www-form-urlencoded",
        })
        print(res.text)

        res_json = json.loads(res.text)

        return "\n".join([x["dst"] for x in res_json["trans_result"]])

    def translate(self, text):
        """
            接口限制请求频率为1秒1次，在这里使用 self.ts 计时并限制
            按接口返回结果的那一刻开始重置计时器
        """
        if not text:
            return ""

        # 纯 特殊符号和数字 组成的字符串直接返回
        if re.match(r"^[0-9|\s\+\-\%\~\!\@\#\$\^\&\*\(\)\_\=\`\[\]\\\{\}\|\;\'\:\"\,\.\/\<\>\?]+$", text, re.I):
            return text

        # cache_key = "%s-%s\t%s" % (self.from_lan, self.to_lan, text)
        cache_key = text  # .replace("\r", "\1").replace("\n", "\2")
        if cache_key in self.cache:
            return self.cache[cache_key]

        if self.ts:
            cool_down = time.time() - self.ts
            if cool_down < self.cool_down_time:
                time.sleep(self.cool_down_time - cool_down)

        self.cache[cache_key] = self.call_baidu_api(text)  # .replace("\r", "\1").replace("\n", "\2")
        self.ts = time.time()
        return self.cache[cache_key]


def init_fanyi(builder, from_lan, to_lan):
    """
        baidu: baidu fanyi
    """
    if builder == "baidu":
        fy = BaiduFanyi(from_lan, to_lan)
    else:
        fy = BaseFanyi(from_lan, to_lan)

    return fy


def test():
    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    fy = init_fanyi("test", from_lan="cn", to_lan="swe")
    # fy = init_fanyi("baidu", from_lan="cn", to_lan="swe")
    text = fy.translate("我想要的一切")
    print("我想要的一切:", text)

    text = fy.translate("圣诞节快乐")
    print("圣诞节快乐:", text)

    text = fy.translate("晚安")
    print("晚安:", text)

    fy.save_result()

    with open("./data/dict_base.ru-zh.log", "r") as rf:
        contents = rf.readlines()
        contents = [x.split("\0")[0].strip() for x in contents]

    with open("/tmp/empty.ru-zh.txt", "w") as wf:

        for lineno, line in enumerate(contents):
            wf.write(line)
            wf.write("\n")


if __name__ == "__main__":
    test()
