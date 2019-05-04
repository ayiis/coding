#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2019/01/01

from flask import Flask, request, send_from_directory
import json
import uuid
import ubelt
import requests
from extract_article import extract_article
from nlp import cut, recognize

UPLOAD_FILE_PATH = "static"
ubelt.ensuredir(UPLOAD_FILE_PATH)

my_app = Flask(__name__)


@my_app.route("/")
@my_app.route("/%s" % UPLOAD_FILE_PATH)
def render(path=None):
    if not path:
        path = "index.html"

    return send_from_directory(UPLOAD_FILE_PATH, "%s" % path)


@my_app.route("/get_start", methods=["post"])
def get_start():

    try:
        url = request.json["url"]
        response = requests.get(url)
        print("url:", url)

        title, article = extract_article(response.content)
        print("title:", title)
        print("article:", article)

        # article = article.replace(" ", "")

        article = article[:520]

        return json.dumps({
            "desc": "success",
            "data": {
                "title": title,
                "article": article
            },
            "code": 200
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return json.dumps({
            "desc": str(e),
            "data": None,
            "code": 200
        })


@my_app.route("/get_cut_and_recognize", methods=["post"])
def get_cut_and_recognize():

    try:
        text = request.json["text"]
        text = text[:520]
        cut_result = cut(text)
        recognize_result = recognize(text)
        print("cut_result:", cut_result)
        print("recognize_result:", recognize_result)

        return json.dumps({
            "desc": "success",
            "data": {
                "recognize": recognize_result,
                "cut": cut_result,
            },
            "code": 200
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return json.dumps({
            "desc": str(e),
            "data": None,
            "code": 200
        })


def make_app():

    my_app.tts_func = {}
    my_app.run(host="0.0.0.0", port=8080, debug=True)
    print("listening %s" % 8080)


if __name__ == "__main__":
    make_app()
