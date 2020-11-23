#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2020/08/11
import asyncio
import aiohttp.web


async def main():

    # 初始化数据库
    import config
    from common import mongodb
    await mongodb.init_connection(config.mongodb_settings)

    # 初始化 jade 页面
    from build import JadeWork
    templete = JadeWork.build("src_jade", "src")

    # 启动 web 服务
    from handlers import ApiHandler, TemplateHandler
    from handlers import test, test_queue

    app = aiohttp.web.Application()
    ApiHandler.add_handlers({
        "/api/test": test.do,
        "/api/test_queue": test_queue.do,
    })

    app.router.add_static("/static/", path="./static/", name="static")  # 静态资源 js css img (下载形式)
    app.router.add_route("POST", "/api/{match:.*}", ApiHandler.do)      # API 接口
    app.router.add_route("GET", "/{match:.*}", TemplateHandler.wrap("src_jade", templete, index="index"))   # html 页面

    await asyncio.gather(
        test_queue.worker(),                    # 后台处理的 worker (通过 queue 传递请求)
        aiohttp.web._run_app(app, port=7001),   # 启动web服务，监听端口
    )


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
