
## 会遇到的几个问题

    1. 前端框架，怎么绑定数据
    2. 前端的模块如何复用
    3. 如何清除浏览器缓存


## 概要 ✖️✅❌⚠️⏱

    ✅ 0. 基于 aiohttp

        🚫 1. 支持 服务器渲染
            禁止

        ⏱ 2. 支持 mongodb
        ⏱ 3. 支持 redis
        ⏱ 3. 支持 异步请求外部地址

    ✅ 1. 支持 jade

        POST: 请求与返回都使用 json 格式
        GET:
            允许访问 static (资源静态下载)
            允许访问 src_jade (jade&html，缓存在内存)

api response:

    _good_code = 0
    _error_code = 500


