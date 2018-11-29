#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
1. 计算输入rgb的灰度

2. 以16为步长枚举所有rgb组合，计算出所有与 目标灰度 差值小于 16 的rgb

3. 输出计算结果

eg:
    背景色 #d0f0f0
    干扰色 #fce0cb
    前景色 #e0f0d0
"""

MAGIC_NUM = 4
STEP_LENGTH = MAGIC_NUM * 4


def gray_1(R, G, B):
    """
        FFF = (1*R + 1*G + 1*B) / 3.0
    """
    return (R + G + B) / 3


def gray_2(R, G, B):
    """
        FFF = (R * 299 + G * 587 + B * 114) / 1000
    """
    return (R * 299 + G * 587 + B * 114) / 1000


def main(R, G, B):

    gray1 = gray_1(R, G, B)
    gray2 = gray_2(R, G, B)

    good_rgb = []

    for r in range(0, 256, STEP_LENGTH):
        for g in range(0, 256, STEP_LENGTH):
            for b in range(0, 256, STEP_LENGTH):
                if -MAGIC_NUM <= gray_1(r, g, b) - gray1 <= MAGIC_NUM:
                    if -MAGIC_NUM <= gray_2(r, g, b) - gray2 <= MAGIC_NUM:
                        good_rgb.append("%02x%02x%02x" % (r, g, b))

    print "origin:", "%02x%02x%02x" % (R, G, B)
    print "similar_rgb:", good_rgb


if __name__ == "__main__":
    R, G, B = 0xfc, 0xe0, 0xcb
    main(R, G, B)
