#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

settings = {
    "proxy.coderbusy.com": {
        "enable": True,
        # "period": 60 * 60 * 24 * 1, # every day
        # "day_of_week": 1, # Monday every week
        "time_of_day": "11:00", # 11:00 everyday
        "request_timeout": 90,
    }
}

validate_setting = {
    "count": 50,    # 每次验证从数据库中取多少个IP()
}

