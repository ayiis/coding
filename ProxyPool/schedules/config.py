#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

setting = {

    "available_pool": {
        "db_name": "available_pool",
        "count": 100,    # 每次验证多少个IP
        "timeout": 15,    # 超时
        "period": 60 * 30,    # 检验周期 30 minutes
    },

    "unavailable_pool": {
        "db_name": "unavailable_pool",
        "count": 100,    # 每次验证多少个IP
        "timeout": 15,    # 超时
        "period": 60 * 60 * 3,    # 检验周期 3 hours
    },

    "fail_pool": {
        "db_name": "fail_pool",
        "count": 100,    # 每次验证多少个IP
        "timeout": 15,    # 超时
        "period": 60 * 60 * 24 * 3,    # 检验周期 3 days
    },

}
