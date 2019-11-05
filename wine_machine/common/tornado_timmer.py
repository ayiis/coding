#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.gen
import datetime
import time


class MinuteTimmer(object):
    """
        run at x minute at every hours
    """
    def __init__(self, callback, minute_list=None):
        super(MinuteTimmer, self).__init__()
        self.minute_list = minute_list or [x * 5 + 1 for x in range(60 // 5)]
        self.callback = callback
        self.last_callback_minute = None
        set_interval(2, self.run)

    def run(self):
        tmin = time.localtime(time.time()).tm_min
        if tmin != self.last_callback_minute and tmin in self.minute_list:
            self.last_callback_minute = tmin
            self.callback()


def sleep(timeout_seconds):
    return tornado.gen.sleep(timeout_seconds)


def set_timeout(timeout_seconds, outter_func):
    return tornado.ioloop.IOLoop.current().add_timeout(tornado.ioloop.IOLoop.current().time() + timeout_seconds, outter_func)


def set_interval(timeout_seconds, outter_func):
    interval_job = tornado.ioloop.PeriodicCallback(outter_func, timeout_seconds * 1000)
    interval_job.start()
    return interval_job


def set_clock(clock, outter_func):
    """
        run function at the same time of day
    """
    next_ts = datetime.datetime.strptime(
        str(datetime.date.today()) + " " + clock, "%Y-%m-%d %H:%M:%S")
    next_ts = time.mktime(next_ts.timetuple())
    next_ts = next_ts - tornado.ioloop.IOLoop.current().time()
    if next_ts < 0:
        next_ts = 60 * 60 * 24 + next_ts

    def _set_clock_callback():
        outter_func()
        return set_interval(60 * 60 * 24, outter_func)
    return set_timeout(next_ts, _set_clock_callback)


def remove_timeout(timeout):
    tornado.ioloop.IOLoop.current().remove_timeout(timeout)


def remove_interval(interval_job):
    interval_job.stop()
