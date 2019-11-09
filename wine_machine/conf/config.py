#!/usr/bin/env python3
# -*- coding: utf-8 -*-

SYSTEM = {
    "listening_port": 60002,
}

MONGODB = {
    "wm": {
        "HOST": "127.0.0.1",
        "PORT": 27017,
        "DATABASE_NAME": "wm",
        "USERNAME": "",
        "PASSWORD": "",
    },
    "rent_a_life": {
        "HOST": "127.0.0.1",
        "PORT": 27017,
        "DATABASE_NAME": "rent_a_life",
        "USERNAME": "",
        "PASSWORD": "",
    },
}

WATCH_DOGS = {
    "jingdong": {
        "enable": True,
        # "period": 60 * 6,  # every x minutes
        "minute_list": [x * 5 + 1 for x in range(60 // 5)],  # run at x minute of every hours
    },
    "kaola": {
        "enable": True,
        # "period": 60 * 7,  # every x minutes
        "minute_list": [x * 7 + 1 for x in range(60 // 7)],  # run at x minute of every hours
    },
    "yanxuan": {
        "enable": True,
        # "period": 60 * 7,  # every x minutes
        "minute_list": [x * 7 + 1 for x in range(60 // 7)],  # run at x minute of every hours
    },
    "douban": {
        "enable": True,
        "period": 60 * 23,  # every x minutes
    },
}

