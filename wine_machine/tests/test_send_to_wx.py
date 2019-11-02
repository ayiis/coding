import tornado.gen
import tornado.ioloop
import sys
sys.path.insert(0, "/mine/github/coding/wine_machine")
from common import tool


@tornado.gen.coroutine
def main():
    try:
        yield tool.send_to_my_wx("title", """
## 大标题
[ **M** ] arkdown + E [ **ditor** ] = **Mditor**
> 在此键入内容，所有的`<html>`标签都会被过滤

[homepage](https://www.baidu.com) baidu
        """)
        tornado.ioloop.IOLoop.current().stop()
    except Exception as e:
        print("e:", e)


if __name__ == "__main__":
    main()
    tornado.ioloop.IOLoop.current().start()
