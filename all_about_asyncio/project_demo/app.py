#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2020/08/11
import re
import asyncio
import aiohttp.web


async def main():

    from handlers import ApiHandler, TemplateHandler
    from handlers import test
    from build import JadeWork

    templete = JadeWork.build("src_jade", "src")

    ApiHandler.add_handlers({
        "/api/test": test.do,
    })

    # 启动 web 服务
    app = aiohttp.web.Application()

    app.router.add_static("/static/", path="./static/", name="static")  # 静态资源 js css img (下载形式)
    app.router.add_route("POST", "/api/{match:.*}", ApiHandler.do)      # API 接口
    app.router.add_route("GET", "/{match:.*}", TemplateHandler.wrap("src_jade", templete))      # html 页面

    await asyncio.gather(
        # video_work.worker(),            # 后台处理的 worker
        aiohttp.web._run_app(app, port=7001),   # 启动web服务，监听端口
    )


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
