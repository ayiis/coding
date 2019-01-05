#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import uuid
import time

import tornado
import tornado.gen
import ubelt
import my_json

from tinydb import TinyDB
db = TinyDB("data/db.json")


class Upload(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):

        upload_file_dir = "upload"
        download_file_dir = "static"
        ubelt.ensuredir(upload_file_dir)
        ubelt.ensuredir(download_file_dir)

        file_metas = self.request.files["csv"]
        # print("file_metas:", file_metas)
        # one file one time
        for meta in file_metas:
            # print("meta:", meta)
            random_name = uuid.uuid4().hex
            file_name = "%s/%s.csv" % (upload_file_dir, random_name)
            with open(file_name, "wb") as wf:
                wf.write(meta["body"])

        self.set_status(200)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.finish("ok")
