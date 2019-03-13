#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ayiis"
# create on 2019/03/07
"""
    可视化音频文件内的各种信息

    ┌───┬───┐
    │ 1 │ 2 │
    ├───┼───┤
    │ 4 │ 3 │
    └───┴───┘

"""


def construct_a_line(data_tuple):
    header_fmt = "┌%s┐"
    content_fmt = "│%s│"
    bottom_fmt = "└%s┘"
    header_string = []
    content_string = []
    bottom_string = []
    for length, text in data_tuple:
        header_string.append("─" * (4 * length - 1))
        bottom_string.append("─" * (4 * length - 1))
        content_string.append(("%%%ss" % (4 * length - 1)) % text)

    return "\r\n".join([
        header_fmt % "┬".join(header_string),
        content_fmt % "│".join(content_string),
        bottom_fmt % "┴".join(bottom_string),
    ])


def test():
    import struct
    WAV_FILE_PATH = "/tmp/wav/16000x6s.wav"

    with open(WAV_FILE_PATH, "rb") as rf:
        wav_content = rf.read(44)

    wav_header = struct.unpack("<4sL4s4siHHiiHH4sL", wav_content)

    print(WAV_FILE_PATH.split("/")[-1], ":", wav_header)

    print("""┌────────┬────────┬─────────┐""")

    print("""│%8s│%8s│%9s│""" % (wav_header[0].decode("utf8"), wav_header[1], wav_header[2].decode("utf8")))

    print("""├────────┼────────┼────┬────┤""")

    print("""│%8s│%8s│%4s│%4s│""" % (wav_header[3].decode("utf8"), wav_header[4], wav_header[5], wav_header[6]))

    print("""├────────┼────────┼────┼────┤""")

    print("""│%8s│%8s│%4s│%4s│""" % (wav_header[7], wav_header[8], wav_header[9], wav_header[10]))

    print("""├────────┼────────┼────┴────┤""")

    print("""│%8s│%8s│%9s│""" % (wav_header[11].decode("utf8"), wav_header[12], "..."))

    print("""└────────┴────────┴─────────┘""")

    print(construct_a_line(zip((4, 4, 4), (wav_header[0].decode("utf8"), wav_header[1], wav_header[2].decode("utf8")))))
    print(construct_a_line(zip((4, 4, 2, 2, 4, 4, 2, 2), (wav_header[3].decode("utf8"), wav_header[4], wav_header[5], wav_header[6], wav_header[7], wav_header[8], wav_header[9], wav_header[10]))))
    print(construct_a_line(zip((4, 4, 4), (wav_header[11].decode("utf8"), wav_header[12], "..."))))


if __name__ == "__main__":
    test()
