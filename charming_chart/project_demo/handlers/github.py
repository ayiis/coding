#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import q
import tornado.web
import tornado.gen
from common.mongodb import DBS
import os
import ubelt
import aytool.common.tool as mytool
import time


def get_weekday_from_datetime(datetime_string):
    return time.strptime(datetime_string[:19], "%Y-%m-%dT%H:%M:%S").tm_wday


@tornado.gen.coroutine
def daily_summary(handler, req_data):
    # start_date = req_data.get("start_date", "2020-01-01")
    # end_date = req_data.get("end_date", "2020-12-31")
    # sequence_name = yield DBS["db_gestureapi"].get_next_sequence("sequence_counters")
    # print("sequence_name:", sequence_name)
    # db_result = yield DBS["db_gestureapi"]["log_%s" % "2020-05-31"].aggregate([{
    #     "$group": {
    #         "_id": {
    #             "$substr": ["$request_time", 0, 2],
    #         },
    #         "c": {
    #             "$sum": 1
    #         }
    #     }
    # }]).to_list(length=None)
    # return [24, 36, 15, 0, 0, 0, 0, 0, 0, 21, 30, 36, 12, 0, 21, 36, 36, 21, 21, 24, 27, 18, 6, 6]

    # return {"daily": [8, 12, 10, 0, 0, 0, 0, 0, 0, 7, 12, 28, 22, 2, 35, 28, 28, 25, 15, 11, 12, 15, 6, 3], "weekly": [47, 53, 60, 58, 33, 19, 9]}

    github_username = req_data.get("github_username") or "ayiis"
    # github_username = req_data.get("github_username") or "iceyang"
    project_list = ["coding", "paper", "aytool", "sock_raw", "ayPass", "vcSources"]
    # project_list = ["leetcode", "iceyang", "go-handbook", "iceyang.github.io", "anki-backup", "xgin", "boom", "gin-exam", "go-collins", "data_structure_and_algorithm", "data_structure_and_algorithm_code", "git-flow-test", "nleveler", "gitalk.keepmoving.ren", "dotfile", "iocfy-ts", "x-accel-redirect-with-nginx", "iocfy-web-example", "iocfy", "docker", "jenkins-pipeline-test", "cgcenter", "nginx-logdb", "blog-web", "blog-ms", "blog-server", "grunt-contrib-nodeunit-demo", "sails_study"]

    result_data = {
        "daily": [0] * 24,
        "weekly": [0] * 7,
    }
    for project in project_list:

        store_path = "%s/%s/%s" % ("store_data", github_username, project)
        if not os.path.isdir(store_path):
            ubelt.ensuredir(store_path)
            mytool.execute_command("git clone --filter=tree:0 --no-checkout https://github.com/%s/%s %s" % (github_username, project, store_path))
        else:
            mytool.execute_command("cd %s && git fetch" % (store_path))

        c_date_list = mytool.execute_command("""cd %s && git log --author="%s" --pretty=format:%%cI""" % (store_path, github_username))
        print("c_date_list:", c_date_list)
        for line in c_date_list.splitlines():
            result_data["daily"][int(line[11:13])] += 1
            result_data["weekly"][get_weekday_from_datetime(line)] += 1

    return result_data
