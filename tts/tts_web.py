#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2019/01/01

from flask import Flask, request, send_from_directory
import json
import uuid
import ubelt

UPLOAD_FILE_PATH = "static"
ubelt.ensuredir(UPLOAD_FILE_PATH)

my_app = Flask(__name__)


@my_app.route("/")
@my_app.route("/%s" % UPLOAD_FILE_PATH)
def render(path=None):
    if not path:
        path = "/static/tts.html"

    return send_from_directory(UPLOAD_FILE_PATH, "%s" % path)


@my_app.route("/do_tts", methods=["post"])
def upfile():

    try:
        text = request.json["text"]
        file_name = "%s/%s.wav" % (UPLOAD_FILE_PATH, uuid.uuid4().hex)
        print("%s: %s", (file_name, text))

        text_label = my_app.create_label(text)
        my_app.tts_func[request.json["tts_name"]](text_label, file_name)

        return json.dumps({
            "desc": "success",
            "data": "/%s" % file_name,
            "code": 200
        })
    except Exception:
        import traceback
        print(traceback.format_exc())

    return json.dumps({
        "desc": "nothing to do",
        "data": None,
        "code": 200
    })


def make_app():

    import main
    my_app.create_label = main.create_label
    my_app.tts_func = {}
    my_app.tts_func["hecuiru"] = main.init("hecuiru")
    my_app.tts_func["15521387651"] = main.init("15521387651")

    my_app.run(host="0.0.0.0", port=8891, debug=False)
    print("listening %s" % 8891)


if __name__ == "__main__":
    make_app()
