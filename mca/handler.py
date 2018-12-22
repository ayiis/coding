#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import tornado
import tornado.gen
import re, traceback
import os
import pickle
import uuid
import random
import time
import copy

import tool
import my_json
import ubelt
import my_comment_analyze

from tinydb import TinyDB, Query
db = TinyDB("data/db.json")

public_db_data = {}

if not db.all():
    db.insert({
        "id": "spzp",
        "name": "尚品宅配",
        "photo": "/static/dist/images/mao.png",
        "data_path": "data/spzp.pkl",
        "data": None,
        "helloworld": [
            "Hello，我是方块猫自动客服助手，我最近在网络上浏览了许多关于尚品宅配的帖子，了解了很多网友对尚品宅配的看法。",
            "如果您想知道网友们的评价，可以这样问我：尚品宅配怎么样？"
        ]
    })

    db.insert({
        "id": "w",
        "name": "W酒店",
        "photo": "/static/dist/images/3.jpg",
        "data_path": "data/w.pkl",
        "data": None,
        "helloworld": [
            "Hello，我是方块猫自动客服助手，我最近在网络上浏览了许多关于W酒店的帖子，了解了很多网友对W酒店的看法。",
            "如果您想知道网友们的评价，可以这样问我：W酒店怎么样？",
        ]
    })


@tornado.gen.coroutine
def init():
    all_items = db.all()
    for item in all_items:
        public_db_data[item["id"]] = item
        with open(item["data_path"], "rb") as rf:
            item["data"] = pickle.load(rf)

    print("load w.data done!")


@tornado.gen.coroutine
def send_message(self, req_data):

    print("ffffff send_message:", req_data)

    res = my_comment_analyze.do_answer(public_db_data[req_data.get("type")]["data"], req_data["text"])

    raise tornado.gen.Return((res, ""))


@tornado.gen.coroutine
def get_item_detail(self, req_data):

    print("ffffff get_item_detail:", req_data)

    all_items = db.all()
    detail = next((x for x in all_items if x.get("id") == req_data.get("type")), {})
    lists = [{
        "photo": x["photo"],
        "id": x["id"],
        "name": x["name"],
    } for x in all_items]

    res = {
        "detail": detail,
        "list": lists,
    }

    raise tornado.gen.Return(res)


class AddOne(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):

        assert self.get_body_argument("name", default=None, strip=True), "请填写名称"
        assert self.get_body_argument("helloworld", default=None, strip=True), "请填写问候语"
        assert self.request.files.get("file"), "请上传文件"

        upload_file_dir = "data"
        ubelt.ensuredir(upload_file_dir)

        file_metas = self.request.files["file"]
        for meta in file_metas[:1]:
            # print("meta:", meta)
            fid = uuid.uuid4().hex
            ts = time.time()
            file_name = "%s/%s.data" % (upload_file_dir, meta["filename"])
            with open(file_name, "wb") as wf:
                wf.write(meta["body"])

            comment_list = my_comment_analyze.get_comment_data_default(file_name)
            print("comment_list:", comment_list)
            nlp_data = my_comment_analyze.prepare_nlp_data(comment_list)

            data_path = "data/%s.pkl" % fid
            with open(data_path, "wb") as wf:
                pickle.dump(nlp_data, wf)

            one = {
                "id": fid,
                "name": self.get_body_argument("name", default=None, strip=True) or fid,
                "photo": "/static/avatars/avatar (%s).png" % random.randint(1, 73),
                "data_path": data_path,
                "data": None,
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                "duration": time.time() - ts,
                "helloworld": [x.strip() for x in re.split(r"\r|\n", self.get_body_argument("helloworld", default=None, strip=True)) if x.strip()],
            }

            db.insert(one)
            print("one:", one)

            public_db_data[fid] = copy.deepcopy(one)
            with open(public_db_data[fid]["data_path"], "rb") as rf:
                public_db_data[fid]["data"] = pickle.load(rf)

        self.set_status(200)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.finish(my_json.json_stringify(one))
