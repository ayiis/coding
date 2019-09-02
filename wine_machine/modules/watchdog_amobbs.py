from common import tool
import tornado
from tornado import gen
from lxml import etree
import q
from pyquery import PyQuery as pq
"""
    需要记录每次变动的历史
    方便查询具体是哪个产品变动了
"""

WEBPAGE = [
    "https://www.amobbs.com/thread-5682512-1-1.html",   # 香港醉心红酒分类汇总，以方便查找心爱美酒 【导航】
    "https://www.amobbs.com/thread-5667632-1-1.html",   # 香港醉心精品洋酒汇总，白兰地，威士忌等 【烈酒】
    "https://www.amobbs.com/thread-5681990-1-1.html",   # 醉心红酒淘宝店amobbs论坛特价信息公布区 【起泡酒】
    "https://www.amobbs.com/thread-5682249-1-1.html",   # 尝鲜，最近搜罗一批经济型葡萄酒，品类丰富多彩！【葡萄酒】
    "https://www.amobbs.com/thread-5638016-1-1.html",   # 香港醉心酒业精选高性价比红酒发布区 【红酒】
    "https://www.amobbs.com/thread-5660507-1-1.html",   # 醉心特色葡萄酒--迷你型，桃红，白葡萄酒，气泡 【甜葡萄酒】
    "https://www.amobbs.com/thread-5672427-1-1.html",   # 特色低度酒。苹果，波特，雪莉，雅文邑鸡尾酒。【杂酒】
    "https://www.amobbs.com/thread-5670528-1-1.html",   # 葡萄牙波特酒，一种小众却不可不知的葡萄酒 【波特酒】
    "https://www.amobbs.com/thread-5676031-1-1.html",   # 雪利酒：装在瓶子里的西班牙阳光-莎士比亚 【雪利酒】
    "https://www.amobbs.com/thread-5638022-1-1.html",   # 分享一些个人比较喜欢的，算高大上的精品葡萄酒 【精品葡萄酒】
]
WEBPAGE_CACHE = {}


def load_cache():
    """
        TODO: load from db or what
    """
    return WEBPAGE_CACHE


def send_message(message):
    """
        TODO: message 结构体，使用 common 里面的公共方法发送 message 到微信or what
    """
    print(message)


@gen.coroutine
def crawler(page_url, retry=True):
    # raise gen.Return( open("test.html", "rb").read() )   # DEBUG
    req_data = {
        "url": page_url,
        "method": "GET",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        },
        "proxy_host": "192.168.206.1",
        "proxy_port": 1080,
        "request_timeout": 30,
    }
    response = yield tool.http_request(req_data)
    if response.code == 599 and retry:
        response = yield tool.http_request(req_data)

    if response.code != 200:
        raise gen.Return("")

    raise gen.Return(response.body)


def parse_content_to_dom(content):
    parser = etree.HTMLParser(encoding="utf-8")
    return pq(etree.fromstring(content, parser=parser))


def iter_eles(elements):
    for i in range(len(elements)):
        yield i, elements.eq(i)


@gen.coroutine
def main():

    WEBPAGE_CACHE.update(load_cache())

    # if True:
    for i in range(3):
        page_url = WEBPAGE[0]
        # result = yield crawler(page_url)

        result = open("test.html", "rb").read()
        # print("result:", result)
        result = result.decode("utf8")

        ehtml = parse_content_to_dom(result)
        content_tds = ehtml.find(".t_fsz").find("td")
        content_texts = [td.text().strip() for i, td in iter_eles(content_tds)]

        # 判断改动
        if WEBPAGE_CACHE.get(page_url) != content_texts:
            content_texts_old = WEBPAGE_CACHE.get(page_url)
            if content_texts_old:
                if len(content_texts) != len(content_texts_old):
                    print("[PAGE] comment amount add: %s" % (len(content_texts) - len(content_texts_old)))

                for i in range(min(len(content_texts), len(content_texts_old))):
                    if content_texts_old[i] != content_texts[i]:
                        print("[COMMENT] comment %s changed." % (i))

            WEBPAGE_CACHE[page_url] = content_texts

        else:
            WEBPAGE_CACHE[page_url][0] = WEBPAGE_CACHE[page_url][0].replace('5672427', '123456')

    q.d()
    tornado.ioloop.IOLoop.current().stop()


if __name__ == "__main__":
    main()
    tornado.ioloop.IOLoop.current().start()
