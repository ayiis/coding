#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    整理爬取的视频结果：
        - 将 mp4 文件直接重命名
        - 将 ts 片段文件组合成一个 ts 文件
            1. 有 key 的 ts 文件先逐个进行 aes-128-cbc 解密再按顺序合并
            2. 无 key 的 ts 文件按顺序合并
"""
"""
    aes-128-cbc测试：

        ffmpeg -i result.ts -bsf:a aac_adtstoasc -acodec copy -vcodec copy result.mp4

        ffmpeg -allowed_extensions ALL -i de.m3u8 -c copy output.ts

    # https://stackoverflow.com/questions/40366617/using-openssl-to-decrypt-a-ts-file

        openssl aes-128-cbc -d -K `xxd -p getDK` -iv 0000000000000000 -in v.f230.ts -out v.f230.out.ecb.ts

    * 调用 ffmpeg 和 openssl 太慢，此处使用自己实现的 aes-128-cbc 文件解密算法

"""
import q
import os
import shutil
import traceback
import re
import ubelt
import sys
from pathlib import Path
from Crypto.Cipher import AES


def aes_file_decrypt(in_file, out_file, key, iv):
    bs = AES.block_size
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = "".encode("utf8")
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = chunk[-1]
            if padding_length < 1 or padding_length > bs:
                raise ValueError("bad decrypt pad (%d)" % padding_length)
            # all the pad-bytes must be the same
            if chunk[-padding_length:] != (padding_length * chr(padding_length)).encode("utf8"):
                # this is similar to the bad decrypt:evp_enc.c from openssl program
                raise ValueError("bad decrypt")
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)


def decrypt_and_join_all_ts(target_path):

    # 已经有 mp4 文件，不再做处理
    if os.path.isfile("%s/%s" % (target_path, "temp.mp4")):
        return ".mp4"

    # 目标ts片段文件
    ts_file_list = []
    for ts in Path(target_path).glob("*.ts"):
        if re.match(r"""[\d]+\.[\d]+\.ts""", ts.name, re.I):
            ts_file_list.append(ts.name)

    ts_file_list.sort(key=lambda x: int(x.split(".")[0]))

    if not ts_file_list:
        print("[Error] no mp4 or ts file is found!")

    # 有 key 需要先解密再拼接
    if os.path.isfile("%s/%s" % (target_path, "temp.key")):
        print("Got key in ", target_path)
        iv = ("\x00" * 16).encode("utf8")
        with open("%s/temp.key" % (target_path), "rb") as rf:
            key = rf.read()

        with open("%s/temp.ts" % (target_path), "wb") as out_file:
            for ts in ts_file_list:
                with open("%s/%s" % (target_path, ts), "rb") as rf:
                    aes_file_decrypt(rf, out_file, key, iv)

    # 无 key 直接拼接
    else:
        print("directly join ", target_path)
        with open("%s/temp.ts" % (target_path), "wb") as out_file:
            for ts in ts_file_list:
                with open("%s/%s" % (target_path, ts), "rb") as rf:
                    out_file.write(rf.read())

    return ".ts"


def main():

    # 原始爬取结果路径
    course_path = "/f_data/dxy/dxy/"
    # 输出整理好的结果
    new_root_dir = "/f_data/dxy_done/"
    save_course_path = []

    # 解密以及拼接
    for course in Path(course_path).glob("*"):

        course_path_name = "%s" % (course)
        if not os.path.isdir(course_path_name):
            continue

        save_course_path.append(course_path_name)

        if os.path.isfile("%s/done.done" % course_path_name):
            print("Target path", course_path_name, "is done")
            continue

        for lesson_path in Path(course_path_name).glob("*"):

            lesson_path_name = "%s" % (lesson_path)
            if not os.path.isdir(lesson_path_name):
                continue
            # break   # TODO

            print("doing:", lesson_path_name)
            try:
                decrypt_and_join_all_ts(lesson_path_name)
                # break   # TODO
            except Exception:
                print(traceback.format_exc())
                print("Target path", course_path_name, lesson_path_name)
                with open("error.log", "a") as af:
                    af.write("%s/%s\n" % (course_path_name, lesson_path_name))

        with open("%s/done.done" % course_path_name, "w") as wf:
            wf.write("")

        # break   # TODO

    # 生成输出的目录的结构
    for old_course_path in save_course_path:
        old_course_path_name = "%s" % (old_course_path)
        new_course_path_name = old_course_path_name.replace(course_path, new_root_dir)
        ubelt.ensuredir(new_course_path_name)

    all_lesson_path = []
    # 补充：遍历处理
    for course in Path(course_path).glob("*"):

        course_path_name = "%s" % (course)
        if not os.path.isdir(course_path_name):
            continue

        for lesson_path in Path(course_path_name).glob("*"):

            lesson_path_name = "%s" % (lesson_path)
            if not os.path.isdir(lesson_path_name):
                continue

            all_lesson_path.append(lesson_path_name)

    # 复制，重命名视频
    print("Total is:", len(all_lesson_path))
    for lesson_path in all_lesson_path:
        lesson_path_name = "%s" % (lesson_path)
        out_fix = ""
        if os.path.isfile("%s/%s" % (lesson_path_name, "/temp.ts")):
            out_fix = ".ts"
        elif os.path.isfile("%s/%s" % (lesson_path_name, "/temp.mp4")):
            out_fix = ".mp4"
        else:
            print("nothing to do:", lesson_path_name)
            continue

        new_lesson_path_name = lesson_path_name.replace(course_path, new_root_dir)
        new_lesson_path_name = "%s%s" % (new_lesson_path_name, out_fix)

        if os.path.isfile(new_lesson_path_name):
            pass
        else:
            # print("copying", "%s/temp%s" % (lesson_path_name, out_fix), "to", new_lesson_path_name)
            shutil.copy("%s/temp%s" % (lesson_path_name, out_fix), new_lesson_path_name)


def make_up_leak():

    # 原始爬取结果路径
    course_path = "/f_data/dxy/dxy/"
    # 输出整理好的结果
    new_root_dir = "/f_data/dxy_done/"

    all_lesson_path = []
    # 补充：遍历处理
    for course in Path(course_path).glob("*"):

        course_path_name = "%s" % (course)
        if not os.path.isdir(course_path_name):
            continue

        for lesson_path in Path(course_path_name).glob("*"):

            lesson_path_name = "%s" % (lesson_path)
            if not os.path.isdir(lesson_path_name):
                continue

            all_lesson_path.append(lesson_path_name)

    # 复制，重命名视频
    print("Total is:", len(all_lesson_path))
    for lesson_path in all_lesson_path:
        lesson_path_name = "%s" % (lesson_path)
        out_fix = ""
        if os.path.isfile("%s/%s" % (lesson_path_name, "/temp.ts")):
            out_fix = ".ts"
            continue
        elif os.path.isfile("%s/%s" % (lesson_path_name, "/temp.mp4")):
            out_fix = ".mp4"
            continue
        else:
            print("nothing to do:", lesson_path_name)
            try:
                out_fix = decrypt_and_join_all_ts(lesson_path_name)
            except Exception:
                print("Error lesson_path_name:", lesson_path_name)
                print(traceback.format_exc())

        new_lesson_path_name = lesson_path_name.replace(course_path, new_root_dir)
        new_lesson_path_name = "%s%s" % (new_lesson_path_name, out_fix)

        if os.path.isfile(new_lesson_path_name):
            print("Not really happen")
            q.d()
        else:
            # print("copying", "%s/temp%s" % (lesson_path_name, out_fix), "to", new_lesson_path_name)
            shutil.copy("%s/temp%s" % (lesson_path_name, out_fix), new_lesson_path_name)


if __name__ == "__main__":
    main()
    # make_up_leak()
