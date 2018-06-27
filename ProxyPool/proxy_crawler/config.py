#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

validate_setting = {
    "count": 100,    # 每次验证从数据库中取多少个IP()
    "timeout": 15,    # 每个IP timeout
}

crawler_setting = {
    # 已经不更新
    "proxy.coderbusy.com": {
        "enable": False,
        "time_of_day": "11:00", # 11:00 everyday
        "request_timeout": 90,

        "collection_name": "proxy.coderbusy.com.ip_date_raw",
        "data_source": "proxy.coderbusy.com",

        "target_page_struct_list": [
            ["https://proxy.coderbusy.com/classical/https-ready.aspx?page=%s", 1, 10],
            ["https://proxy.coderbusy.com/classical/post-ready.aspx?page=%s", 1, 10],
            ["https://proxy.coderbusy.com/classical/anonymous-type/transparent.aspx?page=%s", 1, 10],
            ["https://proxy.coderbusy.com/classical/anonymous-type/anonymous.aspx?page=%s", 1, 10],
            ["https://proxy.coderbusy.com/classical/anonymous-type/highanonymous.aspx?page=%s", 1, 10],
        ],
    },
    #
    "proxy.xicidaili.com": {
        "enable": True,
        "period": 60 * 60 * 2, # every 2 hours
        "request_timeout": 90,

        "collection_name": "proxy.xicidaili.com.ip_date_raw",
        "data_source": "www.xicidaili.com",

        "target_page_struct_list": [
            ["http://www.xicidaili.com/nn/%s", 1, 20],  # 国内高匿
            ["http://www.xicidaili.com/nt/%s", 1, 20],  # 国内透明
            ["http://www.xicidaili.com/wn/%s", 1, 20],  # HTTPS
            ["http://www.xicidaili.com/wt/%s", 1, 20],  # HTTP
        ],
    },
    # 平均每天更新2页
    "proxy.kuaidaili.com": {
        "enable": True,
        "period": 60 * 60 * 6, # every 6 hours
        "request_timeout": 90,

        "collection_name": "proxy.kuaidaili.com.ip_date_raw",
        "data_source": "www.kuaidaili.com",

        "target_page_struct_list": [
            ["https://www.kuaidaili.com/free/inha/%s/", 1, 5],  # 国内高匿代理
            ["https://www.kuaidaili.com/free/intr/%s/", 1, 5],  # 国内普通代理
        ]
    },
    # 一次请求拿5000～10000条数据
    "proxy.66ip.cn": {
        "enable": True,
        "period": 60 * 60 * 4, # every 4 hours
        "request_timeout": 90,

        "collection_name": "proxy.66ip.cn.ip_date_raw",
        "data_source": "www.66ip.cn",

        # FROM http://www.66ip.cn/nm.html
        "target_page_struct_list": [
            ["http://www.66ip.cn/nmtq.php?getnum=10000&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip&y=%s", 1, 1],
        ],
    },
    # 一次请求拿2810条数据
    "proxy.89ip.cn": {
        "enable": True,
        "period": 60 * 60 * 4, # every 4 hours
        "request_timeout": 90,

        "collection_name": "proxy.89ip.cn.ip_date_raw",
        "data_source": "www.89ip.cn",

        # FROM http://www.89ip.cn/ti.html
        "target_page_struct_list": [
            ["http://www.89ip.cn/tqdl.html?num=3000&address=&kill_address=&port=&kill_port=&isp=&#%s", 1, 1],
        ],
    },

    # 只展示1页15条，平均半小时更新1条
    "proxy.ip3366.net": {
        "enable": True,
        "period": 60 * 60 * 4, # every 4 hours
        "request_timeout": 90,

        "collection_name": "proxy.ip3366.net.ip_date_raw",
        "data_source": "www.ip3366.net",

        "target_page_struct_list": [
            ["http://www.ip3366.net/free/", 1, 1],
        ],
    },

    "proxy.cn-proxy.com": {
        "enable": False,
        "period": 60 * 60 * 4, # every 4 hours
        "request_timeout": 90,

        "collection_name": "proxy.cn-proxy.com.ip_date_raw",
        "data_source": "www.cn-proxy.com",

        # 要翻墙
        "gfw": True,

        "target_page_struct_list": [
            ["http://cn-proxy.com/", 1, 1],
            ["http://cn-proxy.com/archives/218", 1, 1],
        ],
    },

    "proxy.us-proxy.org": {
        "enable": True,
        "period": 60 * 30, # every 30 minutes
        "request_timeout": 90,

        "collection_name": "proxy.us-proxy.org.ip_date_raw",
        "data_source": "www.us-proxy.org",

        # 要翻墙
        # "gfw": True,

        # www.us-proxy.org == free-proxy-list.net
        "target_page_struct_list": [
            ["https://www.us-proxy.org/", 1, 1],
            ["https://www.us-proxy.org/anonymous-proxy.html", 1, 1],
        ],
    },

    # google recaptcha V1
    "proxy.freeproxylists.net": {
        "enable": False,
        "period": 60 * 30, # every 30 minutes
        "request_timeout": 90,

        "collection_name": "proxy.freeproxylists.net.ip_date_raw",
        "data_source": "www.freeproxylists.net",

        # 要翻墙
        "gfw": True,

        "target_page_struct_list": [
            ["http://www.freeproxylists.net/zh/?page=%s", 1, 20],   # 10
        ],
    },

}
