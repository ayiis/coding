import q
import re
import uuid
import asyncio
import traceback
from pyppeteer import launch
from urllib.parse import urlparse


async def fff(interceptedRequest, rand_str):

    try:

        url = urlparse(interceptedRequest.url)

        # if url.netloc[-11:] == ".google.com":
        if url.netloc == "apis.google.com":
            print("[ABORT]", url)
            await interceptedRequest.abort()

        elif url.path == "/" + rand_str:
            print("[INSERT]", url)
            with open("./../data/jquery.min.js", "r") as rf:
                await interceptedRequest.respond({
                    "status": 200,
                    "body": rf.read(),
                })

        else:
            await interceptedRequest.continue_()

    except Exception:
        print(traceback.format_exc())


async def main():
    args = {
        "headless": True, "devtools": False,
        # "headless": False, "devtools": True,
        # "headless": False, "devtools": False,
        "executablePath": "/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome",
        "userDataDir": "/tmp/tmp",
        "ignoreHTTPSErrors": True,
        "args": [
            "--proxy-server=",
            "--proxy-bypass-list=",
        ],
        "defaultViewport": False,
        # "ignoreDefaultArgs": ["--enable-automation"],
        # "args": ["--disable-infobars"],
        # "executablePath": executablePath
    }
    rand_str = uuid.uuid4().hex

    browser = await launch(**args)
    pages = await browser.pages()
    page = pages[0]

    await page.setRequestInterception(True)
    page.on('request', lambda x: fff(x, rand_str))

    # await page.goto('https://translate.google.cn/', waitUntil='networkidle2', timeout=1000 * 60)
    await page.goto('https://translate.google.cn/#view=home&op=translate&sl=ru&tl=zh-CN', waitUntil='networkidle2', timeout=1000 * 60)
    # await page.goto('https://www.baidu.com/', waitUntil='networkidle2')
    await page.reload(waitUntil='networkidle2')

    print("Load ok.")

    # 插入 jquery
    await page.evaluate("""rand_str => {
        document.body.appendChild(document.createElement('script')).setAttribute('src', rand_str);
        return true;
    }""", rand_str)
    await page.waitForResponse(lambda res: urlparse(res.url).path == "/" + rand_str and res.status == 200)

    print("Done insert jquery")

    # # 选原文 语言
    # button_from = '.sl-more.tlid-open-source-language-list'
    # await page.waitForSelector(button_from, visible=True)
    # await page.click(button_from, delay=20)
    # await asyncio.sleep(0.2)
    # # 选
    # button_select_fl = '.language-list-unfiltered-langs-sl_list .language_list_item_wrapper.language_list_item_wrapper-ru'
    # # button_select_fl = '.language_list_item_wrapper.language_list_item_wrapper-ru.item-selected.item-emphasized'
    # await page.waitForSelector(button_select_fl, visible=True)
    # await page.click(button_select_fl, delay=20)

    # print("Click:", "选原文 = ru")
    # await asyncio.sleep(0.5)

    # # 选译文 语言
    # button_to = '.tl-more.tlid-open-target-language-list'
    # await page.waitForSelector(button_to, visible=True)
    # await page.click(button_to, delay=20)
    # await asyncio.sleep(0.2)

    # # 选 因为同样的class有2个。。
    # button_select_tl = '.language-list-unfiltered-langs-tl_list .language_list_item_wrapper.language_list_item_wrapper-zh-CN .language_list_item.language_list_item_language_name'
    # # button_select_tl = '.language_list_item_wrapper.language_list_item_wrapper-zh-CN.item-selected.item-emphasized'
    # await page.waitForSelector(button_select_tl, visible=True)
    # await page.click(button_select_tl, delay=20)

    print("Click:", "选译文 = zh")
    await asyncio.sleep(0.2)

    # await page.waitForFunction('$(".select-from-language .language-selected").text().trim() === "瑞典语"')
    await page.click('#source', delay=20)

    # await page.keyboard.type('baidu.com')

    # await page.keyboard.type('рыцарь\r\n' * 20)

    # def funk(el):
    #     el.value = 'рыцарь\r\nрыцарь'

    # await page.Jeval('#source', '(el => el.value="рыцарь\r\nрыцарь")')
    # await page.querySelectorEval('#source', 'node => node.value="рыцарь\r\nрыцарь"')

    # assert (await feedHandle.JJeval('.tweet', '(nodes => nodes.map(n => n.innerText))')) == ['Hello!', 'Hi!']

    # with open("/tmp/up/note1.txt", "r") as rf:
    with open("/tmp/up/empty.ru-zh.txt", "r") as rf:
        dict_contents = rf.readlines()
        dict_contents = set([line.strip() for line in dict_contents])

    with open("/tmp/up/note2.txt", "r") as rf:
        dict_contents2 = rf.readlines()
        dict_contents2 = set([line.split("\0")[0] for line in dict_contents2])

    todo_dict_contents = dict_contents - dict_contents2
    todo_dict_contents = list(todo_dict_contents)

    todo_count = len(todo_dict_contents)
    print("todo dict:", todo_count)

    with open("/tmp/up/note2.txt", "a") as wf:
        req_len = 0
        req_count = 0
        cache_req = []
        for lineno, line in enumerate(todo_dict_contents):
            try:

                req_len += len(line)
                req_count += 1
                cache_req.append(line)
                if req_len < 1000 and lineno < len(todo_dict_contents) - 1:
                    continue

                req_string = "\\n".join(cache_req)
                req_string = req_string.replace("\n", "\\n").replace("\r", "\\r")
                req_string = req_string.replace("\"", "\'")     # 替换双引号为单引号, js注意
                print("req_len:", req_count, req_len, len(req_string))

                await asyncio.sleep(0.5)
                # await page.click('#source', delay=20)

                # 清空翻译框
                await page.evaluate("""() => {
                    $('#source').val(null);
                }""")
                await asyncio.sleep(1)
                # while True:
                #     await asyncio.sleep(0.5)
                #     contents = await page.evaluate("""() => {
                #         return $('.result-shield-container.tlid-copy-target>.tlid-translation.translation').find('span').map(function(){ return $(this).text() }).toArray().join('\\r\\n');
                #     }""")
                #     if len(contents) <= 1:
                #         break

                # 开始翻译
                print("开始翻译:", len(req_string))
                await page.evaluate("""() => {
                    $("#source").val("%s");
                }""" % (req_string))

                while True:
                    await asyncio.sleep(2)

                    # $('.tlid-translation.translation')
                    # $('.result-shield-container.tlid-copy-target>.tlid-translation.translation')
                    # return $('.result-shield-container.tlid-copy-target>.tlid-translation.translation').find('span').map(function(){ return $(this).text() }).toArray().join('\\r\\n');
                    contents = await page.evaluate("""() => {
                        return $('.result-shield-container.tlid-copy-target>.tlid-translation.translation').html();
                    }""")

                    # q.d()
                    contents = re.sub(r"\<[\/]?span[^\>]*\>", "", contents, flags=re.I)
                    # contents = contents.replace("</span>", "").replace("<span>", "").split("<br>")

                    print("in contents:", len(contents))

                    if "\0" in contents:
                        print("God damn hell!")
                        contents = contents.replace("\0", "\t")

                    if len(contents) > 1:
                        content_list = contents.split("<br>")
                        # content_list = contents.split("\r\n")
                        if len(content_list) == req_count:
                            break
                        else:
                            print("Still waiting?", len(content_list), "/", req_count)

                print("content list:", len(content_list))
                for key_value in zip(cache_req, content_list):
                    wf.write("%s\0%s\n" % key_value)

                todo_count -= req_count

                cache_req = []
                req_len = 0
                req_count = 0

                print("Done once..  left:", todo_count)
                await asyncio.sleep(1)

            except Exception:
                print(traceback.format_exc())
                await asyncio.sleep(5)

    await asyncio.sleep(30)
    await browser.close()


def test():
    asyncio.get_event_loop().run_until_complete(main())


if __name__ == "__main__":
    test()
