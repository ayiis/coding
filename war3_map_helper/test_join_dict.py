import q
import re
import os


def main(args):
    with open(args["file1"], "r") as rf:
        content1 = rf.readlines()
    print("len content1:", len(content1))

    with open(args["file2"], "r") as rf:
        content2 = rf.readlines()
    print("len content2:", len(content2))

    re_line = []
    got_key = set([])
    for i, content in enumerate(content1):
        if not content:
            continue
        content_key = content.split("\x00")[0]
        if content_key not in got_key:
            re_line.append(content)
            got_key.add(content_key)

    for i, content in enumerate(content2):
        if not content:
            continue
        content_key = content.split("\x00")[0]
        if content_key not in got_key:
            re_line.append(content)
            got_key.add(content_key)

    print("len content3:", len(re_line))
    with open(args["file3"], "w") as wf:
        for content in re_line:
            wf.write(content)


if __name__ == "__main__":
    main({
        "file1": "/mine/github/coding/war3_map_helper/data/dict_base.en-zh.log.old",
        "file2": "/mine/github/coding/war3_map_helper/data/dict_base.en-zh.log",
        "file3": "/mine/github/coding/war3_map_helper/data/dict_base.en-zh.txt",
    })
