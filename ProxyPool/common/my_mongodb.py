#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
""" MONGODB 数据库连接 """

import tornado.gen
from motor.motor_tornado import MotorClient

@tornado.gen.coroutine
def init(mongodb_config):
    try:
        my_world_star_dbs = {}
        authenticate_list = []

        for db_name in mongodb_config:
            db = mongodb_config[db_name]
            my_world_star_dbs[db_name] = MotorClient(db["HOST"], db["PORT"])[ db["DATABASE_NAME"] ]
            # authenticate_list.append(my_world_star_dbs[db_name].authenticate(db["USERNAME"], db["PASSWORD"] ))

            setattr(my_world_star_dbs[db_name], "get_next_sequence", lambda sequence_name: get_next_sequence(my_world_star_dbs[db_name], sequence_name))

        yield authenticate_list
    except Exception as e:
        import traceback
        print traceback.format_exc()
    else:
        raise tornado.gen.Return(my_world_star_dbs)


@tornado.gen.coroutine
def get_next_sequence(dbname, sequence_name):
    doc = yield dbname.sequence_counters.find_and_modify(
        query={"_id": sequence_name},
        update={"$inc": {"sequence_value": 1}},
        upsert=True
    )
    if doc is None:
        doc = {"sequence_value": 0}

    raise tornado.gen.Return(str(doc["sequence_value"]))
