#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    默认是同步的，因为redis非常快，封装一层ioloop反而影响性能

    但如果tornado里的redis的包被DROP了，会卡死整个ioloop（超过半小时）
"""
import redis
# from rediscluster import StrictRedisCluster

key_prefix = "WORLD_START_PLATFORM_"
rc = None


def init(HOST, PORT, PASSWD, DB):
    global rc
    pool = redis.ConnectionPool(host=HOST, port=PORT, db=DB, socket_connect_timeout=0.1, socket_timeout=0.1)
    rc = redis.Redis(connection_pool=pool)


def init_cluster():
    global rc
    startup_nodes = [
        {"host": "192.168.28.60", "port": "6379", "password": "worldstar001"},
        {"host": "192.168.28.61", "port": "6379", "password": "worldstar001"},
        {"host": "192.168.28.62", "port": "6379", "password": "worldstar001"},
    ]
    # https://github.com/Grokzen/redis-py-cluster/blob/unstable/rediscluster/client.py
    # RedisClusterRequestTTL=16(hardcode in rediscluster=1.3.4), will retry 16 times when failed.
    StrictRedisCluster.RedisClusterRequestTTL = 2
    rc = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=False, socket_timeout=0.1, socket_connect_timeout=0.1)


def set(key, value, seconds=None):
    try:
        return rc.set(key_prefix + key, value, seconds)
    except Exception as e:
        print "Redis set error:", str(e)

    return None


def get(key):
    try:

        return rc.get(key_prefix + key)
    except Exception as e:
        print "Redis get error:", str(e)

    return None


def exists(key, seconds=None):
    try:
        return rc.exists(key_prefix + key)  # 存在返回1，不存在返回0
    except Exception as e:
        print "Redis exists error:", str(e)

    return None


def llen(key):
    try:
        return rc.llen(key_prefix + key)
    except Exception as e:
        print "Redis llen error:", str(e)

    return None


def lpop(key):
    try:
        return rc.lpop(key_prefix + key)
    except Exception as e:
        print "Redis lpop error:", str(e)

    return None


def lpush(key, value):
    try:
        return rc.lpush(key_prefix + key, value)
    except Exception as e:
        print "Redis lpush error:", str(e)

    return None


def create_pipe():
    try:
        # return rc.pipeline(transaction=False)
        return rc.pipeline()
    except Exception as e:
        print "Redis create_pipe error:", str(e)

    return None


def pipe_get(pipe, key):
    try:
        if not isinstance(pipe, redis.client.Pipeline):
            raise Exception("error@pipe_set->wrong type of pipe")
        pipe.get(key_prefix + key)
    except Exception as e:
        print "Redis pipe_get error:", str(e)


def pipe_set(pipe, key, value, seconds):
    try:
        if not isinstance(pipe, redis.client.Pipeline):
            raise Exception("error@pipe_set->wrong type of pipe")
        pipe.set(key_prefix + key, value, seconds)
    except Exception as e:
        print "Redis pipe_set error:", str(e)


def pipe_execute(pipe):
    try:
        if not isinstance(pipe, redis.client.Pipeline):
            raise Exception("error@pipe_set->wrong type of pipe")
        return pipe.execute()
    except Exception as e:
        print "Redis pipe_execute error:", str(e)

    return None


def ttl(key):
    try:
        return rc.ttl(key_prefix + key)
    except Exception as e:
        print "Redis ttl error:", str(e)

    return None


import tornado
import tornado.gen

import traceback
import tornado.ioloop
import datetime


@tornado.gen.coroutine
def main():
    try:
        print "in main:"
        yield do()
    except Exception:
        print traceback.format_exc()


@tornado.gen.coroutine
def main2():
    while 1:
        print "main2.1"
        yield tornado.gen.sleep(1)


@tornado.gen.coroutine
def do():
    try:
        for i in xrange(500):
            print "in do set/get"
            dt = datetime.datetime.now()
            akey = str(i) + "----" + str(dt)
            try:
                print "set_result:", set(akey, "value:" + akey, seconds=5)
                print "set_result:", set(akey, "value:" + akey, seconds=5)
                print "get_result:", get(akey)
                print "get_result:", get(akey)
            except Exception:
                print traceback.format_exc()
            print "total_seconds:", (datetime.datetime.now() - dt).total_seconds()
            yield tornado.gen.sleep(6)
            print "sleep ok."
            get_result = get(akey)
            print "get_result after sleep:", get_result

        tornado.ioloop.IOLoop.current().stop()
    except Exception:
        print traceback.format_exc()


if __name__ == "__main__":
    try:
        # init("192.168.28.202", 6379, "worldstar001", 3)
        init("127.0.0.1", 6379, None, 3)
        # init_cluster()
        main()
        main2()
        tornado.ioloop.IOLoop.current().start()
    except Exception:
        print traceback.format_exc()
