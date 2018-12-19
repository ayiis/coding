#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    利用时间差来防止多个实例同时启动
    在指定的时间差内，只允许一个实例运行

    第一个实例启动时
    1. 查找小于当前秒 99999990001 的 对应 counter_id，并更新对应 counter_id 的秒数为 99999990006
    2. 如果不存在则插入对应 counter_id，秒数为 99999990006

    第N个实例启动时（通常会在2秒内）
    1. 查找小于当前秒 99999990001~99999990003 < 99999990006 的 对应 counter_id，不存在，插入对应counter_id，DuplicateKey 失败
"""
import time
import traceback
import tornado.gen


@tornado.gen.coroutine
def init(db):
    try:
        time_start = int(time.time())
        yield db.counters.find_and_modify(
            query={"_id": "cronjob_auto_refresh_exchange_rate", "time_start": {"$lt": time_start}},
            update={"$set": {"time_start": time_start + 5}},
            upsert=True
        )
        print "do something..."

    except Exception, e:
        if e.details["codeName"] == "DuplicateKey":
            print "[INFO] 已经有一个实例在工作"
        else:
            print "[ERROR] 数据库连接失败: 任务初始化失败"
            print traceback.format_exc()
