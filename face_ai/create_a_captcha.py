#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

    WIDTH * HEIGHT

    5
    5 28 5 5 28 5 5 28 5 5 28 5
    5

    1. create width137 * height63

    2. chose random letter

    3. got its struct

    4. chose colors from anit-gray

    5. fill struct with colors

    6. paint the image
"""
import numpy as np
import random
from PIL import Image

STRUCT7 = {
    "TOP": None,
    "LTOP": None,
    "LBOTTOM": None,
    "CENTER": None,
    "RTOP": None,
    "RBOTTOM": None,
    "BOTTOM": None,
}

DIGIT_STRUCT = {
    "0": ["TOP", "LTOP", "LBOTTOM", "RTOP", "RBOTTOM", "BOTTOM"],
    "1": ["RTOP", "RBOTTOM"],
    "2": ["TOP", "LBOTTOM", "CENTER", "RTOP", "BOTTOM"],
    "3": ["TOP", "CENTER", "RTOP", "RBOTTOM", "BOTTOM"],
    "4": ["LTOP", "CENTER", "RTOP", "RBOTTOM"],
    "5": ["TOP", "LTOP", "CENTER", "RBOTTOM", "BOTTOM"],
    "6": ["TOP", "LTOP", "LBOTTOM", "CENTER", "RBOTTOM", "BOTTOM"],
    "7": ["TOP", "RTOP", "RBOTTOM"],
    "8": ["TOP", "LTOP", "LBOTTOM", "CENTER", "RTOP", "RBOTTOM", "BOTTOM"],
    "9": ["TOP", "LTOP", "CENTER", "RTOP", "RBOTTOM", "BOTTOM"],
}

DIGIT = {"0": None, "1": None, "2": None, "3": None, "4": None, "5": None, "6": None, "7": None, "8": None, "9": None}


def print_array(arr):
    arr = arr.astype("str").tolist()
    for l in arr:
        print " ".join(l)


def prepare_struct():
    base = np.zeros((28, 5), dtype=int)
    base += 1
    for x, col in enumerate(base):
        for y, row in enumerate(col):
            if x <= y or x >= len(base) - y - 1:
                base[x][y] = 0

    STRUCT7["LTOP"] = base.copy()
    STRUCT7["LBOTTOM"] = STRUCT7["LTOP"].copy()

    STRUCT7["RTOP"] = (base[:, ::-1]).copy()
    STRUCT7["RBOTTOM"] = STRUCT7["RTOP"].copy()

    STRUCT7["TOP"] = base.T.copy()
    STRUCT7["BOTTOM"] = base.T[::-1]
    base = np.zeros((28, 5), dtype=int)
    base += 1
    for x, col in enumerate(base):
        for y, row in enumerate(col):
            if x < y or x > len(base) - y - 1:
                base[x][y] = 0

    STRUCT7["CENTER"] = (base.T[::-1] | base.T).copy()


def prepare_color():

    MAGIC_NUM = 2
    STEP_LENGTH = 8

    def gray_1(R, G, B):
        return (R + G + B) / 3

    def gray_2(R, G, B):
        return (R * 299 + G * 587 + B * 114) / 1000

    def fc(R, G, B):
        s = (R + G + B) / 3
        return (R-s)**2 + (G-s)**2 + (B-s)**2

    def dc(c1, c2):
        return (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2

    while 1:
        while 1:
            R, G, B = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            if fc(R, G, B) > 64**2:
                break

        gray1 = gray_1(R, G, B)
        gray2 = gray_2(R, G, B)

        good_rgb = []

        for r in range(0, 256, STEP_LENGTH):
            for g in range(0, 256, STEP_LENGTH):
                for b in range(0, 256, STEP_LENGTH):
                    if -MAGIC_NUM <= gray_1(r, g, b) - gray1 <= MAGIC_NUM:
                        if -MAGIC_NUM <= gray_2(r, g, b) - gray2 <= MAGIC_NUM:
                            good_rgb.append((r, g, b))
                            # good_rgb.append("%02x%02x%02x" % (r, g, b))

        # print "origin:", "%02x%02x%02x" % (R, G, B)
        # print "similar_rgb:", good_rgb

        fc_good = [fc(*i) for i in good_rgb]
        font_color = good_rgb[fc_good.index(max(fc_good))]
        background_color = good_rgb[fc_good.index(min(fc_good))]
        # print "font color:", font_color
        # print "background color:", background_color
        dc_good = [dc(i, font_color) for i in good_rgb]     # bigger is better
        dc_bad = [dc(i, background_color) for i in good_rgb]    # bigger is better
        evil_color = None

        dc_good_sorted = sorted(dc_good)
        dc_bad_sorted = sorted(dc_bad)

        for i in range(len(dc_good_sorted)):
            if dc_good_sorted[i] == dc_bad_sorted[-i-1]:
                evil_color = good_rgb[dc_good.index(dc_good_sorted[i])]
                break

        if evil_color:
            return [font_color, background_color, evil_color]


def prepare_digit():

    for d in DIGIT_STRUCT:
        base = np.zeros((53, 28), dtype=int)

        base[:5, :28] += (("TOP" in DIGIT_STRUCT[d]) or 2) * STRUCT7["TOP"]
        base[-5:, -28:] += (("BOTTOM" in DIGIT_STRUCT[d]) or 2) * STRUCT7["BOTTOM"]
        base[:28, :5] += (("LTOP" in DIGIT_STRUCT[d]) or 2) * STRUCT7["LTOP"]
        base[:28, -5:] += (("RTOP" in DIGIT_STRUCT[d]) or 2) * STRUCT7["RTOP"]
        base[-28:, :5] += (("LBOTTOM" in DIGIT_STRUCT[d]) or 2) * STRUCT7["LBOTTOM"]
        base[-28:, -5:] += (("RBOTTOM" in DIGIT_STRUCT[d]) or 2) * STRUCT7["RBOTTOM"]
        base[24:29, :] += (("CENTER" in DIGIT_STRUCT[d]) or 2) * STRUCT7["CENTER"]

        DIGIT[d] = base.copy()


def prepare_image(color):
    digit = [str(random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])) for i in range(4)]
    print "digit:", "".join(digit)
    print "color:", " ".join(["%02x%02x%02x" % (r, g, b) for (r, g, b) in color])
    number = [DIGIT[i] for i in digit]
    base = np.zeros((63, 137), dtype=int)
    a, b = 5, 28+5
    base[5:5+53, a:b] += number[0]
    a += 28+5
    b += 28+5
    base[5:5+53, a:b] += number[1]
    a += 28+5
    b += 28+5
    base[5:5+53, a:b] += number[2]
    a += 28+5
    b += 28+5
    base[5:5+53, a:b] += number[3]

    target = np.arange(63*137*3).reshape(63, 137, 3)
    # R G B
    target[base > 1] = color[2]     # [0x10, 0x90, 0xa0]  # 干扰色
    target[base == 1] = color[0]    # [0xa6, 0x5b, 0x37]  # 前景色
    target[base == 0] = color[1]    # [0x70, 0x70, 0x60]  # 背景色

    im2 = Image.fromarray(np.uint8(target))
    im2.show()
    im2.save("number_%s.png" % "".join(digit))


def main():
    prepare_struct()
    prepare_digit()
    color = prepare_color()
    prepare_image(color)


if __name__ == "__main__":
    main()
