#!/usr/bin/env python3
# -*- coding: utf-8 -*-

SYSTEM = {
    "listening_port": 60003,
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
        "period": 60 * 6,  # every 6 minutes
    },
    "douban": {
        "enable": True,
        "period": 60 * 10,  # every 10 minutes
    },
}

