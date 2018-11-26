#!/usr/bin/env python
# -*- coding: utf-8 -*-
# From http://stevehanov.ca/blog/index.php?id=62

import sys
from PIL import Image
import numpy as np
import time

reload(sys).setdefaultencoding("utf8")


class Image_t:
    width = 0
    height = 0
    # RGB format. Least significant byte is R. Most significant is unused.
    data = [0]


GetRValue = lambda a: (a & 0xff)
GetGValue = lambda a: ((a >> 8) & 0xff)
GetBValue = lambda a: (((a) >> 16) & 0xff)
GetAnyValue = lambda a, c: (((a) >> (c*8)) & 0xff)
RGB = lambda r, g, b: (((int)(r)) | ((int)(g) << 8) | ((int)(b) << 16))


# save png file.
def image_save(image, filename=""):
    row_ptr = np.arange(image.height*image.width*3).reshape(image.height, image.width, 3)
    for y in range(image.height):
        for x in range(image.width):
            clr = image_get_pixel(image, x, y)

            row_ptr[y][x] = [(clr) & 0xff, (clr >> 8) & 0xff, (clr >> 16) & 0xff]

            if 250 < x < 256 and 250 < y < 256:
                print y, x, "[", row_ptr[y][x], "]"

    im2 = Image.fromarray(np.uint8(row_ptr))
    # im2.show()
    im2.save(filename)


# load a new image from png file.
def image_load(file_name=""):
    im = Image.open(file_name)
    width, height = im.size
    row_pointers = np.asarray(im, np.int32)
    row_pointers.flags.writeable = True

    row_pointers = row_pointers[:, :, :3]

    image = image_create(width, height)

    for y in range(height):
        for x in range(width):
            # if x == 111:
            #     print "x,y,rgb:", x, y, row_pointers[y][x], RGB(*row_pointers[y][x])
                # raw_input()
            image_set_pixel(image, x, y, RGB(*row_pointers[y][x]))

    return image


def image_set_pixel(image, x=0, y=0, clr=0):

    if (x < 0 or x >= image.width or y < 0 or y >= image.height):
        return

    image.data[y*image.width+x] = clr


def image_get_pixeld(image, x=0, y=0, channel=0):

    if (x < 0 or x >= image.width or y < 0 or y >= image.height):
        return 0

    return GetAnyValue(image.data[y*image.width+x], channel)/255.0


# retrieve the RGB packed pixel value.
def image_get_pixel(image, x=0, y=0):

    if (x < 0 or x >= image.width or y < 0 or y >= image.height):
        return 0

    return image.data[y*image.width+x]


def image_destroy(image):
    image = None


def image_create(width=0, height=0):
    image = Image_t()

    image.data = [0] * width * height
    image.width = width
    image.height = height
    return image


# only reads red channel, assumes green and blue have same value.
# crashes if all pixels are same colour.
def image_sobel(inn, out ):
    buff = [0] * inn.width*inn.height
    m_i_n = 1.0
    m_a_x = 0.0

    x, y, ch = 0, 0, 0
    # for each row, column, and colour channel,
    for y in range(1, inn.height-2):
        for x in range(1, inn.width-2):
            gx = (
                1.0 * image_get_pixeld(inn, x-1, y-1, 0) - 1.0 * image_get_pixeld(inn, x+1, y-1, 0) +
                2.0 * image_get_pixeld(inn, x-1, y, 0  ) - 2.0 * image_get_pixeld(inn, x+1, y, 0  ) +
                1.0 * image_get_pixeld(inn, x-1, y+1, 0) - 1.0 * image_get_pixeld(inn, x+1, y+1, 0)
            )

            gy = (
                1.0 * image_get_pixeld(inn, x-1, y-1, 0) - 1.0 * image_get_pixeld(inn, x-1, y+1, 0) +
                2.0 * image_get_pixeld(inn, x  , y-1, 0) - 2.0 * image_get_pixeld(inn, x  , y+1, 0) +
                1.0 * image_get_pixeld(inn, x+1, y-1, 0) - 1.0 * image_get_pixeld(inn, x+1, y+1, 0)
            )

            val = pow(gx*gx+gy*gy, 0.5)
            buff[y*inn.width+x] = val
            if (val > m_a_x):
                m_a_x = val
            if (val < m_i_n):
                m_i_n = val

    for y in range(inn.height):
        for x in range(inn.width):
            val = 1.0 * (buff[y*inn.width+x] - m_i_n) / (m_a_x-m_i_n) * 255
            image_set_pixel(out, x, y, RGB(val, val, val))


# only reads red channel, assumes green and blue have same value.
# crashes if all pixels are same colour.
def image_sobel_colour(inn, out):

    buff = [0]*inn.width*inn.height
    m_i_n = 1.0
    m_a_x = 0.0

    x, y, ch = 0, 0, 0
    for y in range(1, inn.height-2):
        for x in range(1, inn.width-2):

            # if x != 49 or y != 54:
            #     continue

            # print "x, y:", x, y

            # inn.data[y][x]

            gx = (
                1.0 * colour_difference(image_get_pixel(inn, x-1, y-1), image_get_pixel(inn, x+1, y-1)) +
                2.0 * colour_difference(image_get_pixel(inn, x-1, y  ), image_get_pixel(inn, x+1, y  )) +
                1.0 * colour_difference(image_get_pixel(inn, x-1, y+1), image_get_pixel(inn, x+1, y+1))
            )

            gy = (
                1.0 * colour_difference(image_get_pixel(inn, x-1, y-1), image_get_pixel(inn, x-1, y+1)) +
                2.0 * colour_difference(image_get_pixel(inn, x  , y-1), image_get_pixel(inn, x  , y+1)) +
                1.0 * colour_difference(image_get_pixel(inn, x+1, y-1), image_get_pixel(inn, x+1, y+1))
            )

            val = pow(gx*gx+gy*gy, 0.5)
            buff[y*inn.width+x] = val
            if (val > m_a_x):
                m_a_x = val
            if (val < m_i_n):
                m_i_n = val

    for y in range(inn.height):
        for x in range(inn.width):
            val = 1.0 * (buff[y*inn.width+x] - m_i_n) / (m_a_x-m_i_n) * 255
            image_set_pixel(out, x, y, RGB(val, val, val))


def colour_difference(rgb1=0, rgb2=0):
    Luv1 = np.array([0, 0, 0])
    Luv2 = np.array([0, 0, 0])

    SQR = lambda x: ((x)*(x))

    f1 = [GetRValue(rgb1)/255.0, GetGValue(rgb1)/255.0, GetBValue(rgb1)/255.0]
    f2 = [GetRValue(rgb2)/255.0, GetGValue(rgb2)/255.0, GetBValue(rgb2)/255.0]

    # print "rgb1, rgb2:", (rgb1, rgb2)

    if not (0 == f1[0] == f1[1] == f1[2]):
        convert_sRGB_Luv(f1, Luv1)
    if not (0 == f2[0] == f2[1] == f2[2]):
        convert_sRGB_Luv(f2, Luv2)

    return np.linalg.norm(Luv2 - Luv1)


def convert_sRGB_Luv(rgb=[], Luv=[]):
    XYZ = [0, 0, 0]
    convert_sRGB_XYZ(rgb, XYZ)
    # print "rgb:", rgb, " => ", XYZ
    convert_XYZ_Luv(XYZ, Luv)


class xyz:
    Xr = 1.0/3
    Yr = 1.0/3
    Zr = 1.0/3
    usr = 4.0 * Xr / (Xr + 15 * Yr + 2 * Zr)
    vsr = 9.0 * Yr / (Xr + 15 * Yr + 3 * Zr)
    e = 216.0 / 24389
    k = 24389.0 / 27


ffff = {
    "xyz": xyz()
}


def convert_XYZ_Luv(XYZ=[], Luv=[]):
    yr = 1.0 * XYZ[1] / ffff["xyz"].Yr
    us = 4.0 * XYZ[0] / (XYZ[0] + 15 * XYZ[1] + 3 * XYZ[2])
    vs = 9.0 * XYZ[1] / (XYZ[0] + 15 * XYZ[1] + 3 * XYZ[2])

    if yr > ffff["xyz"].e:
        Luv[0] = 116.0 * pow(yr, 1.0/3) - 16
    else:
        Luv[0] = 1.0 * ffff["xyz"].k * yr

    Luv[1] = 13.0 * Luv[0] * (us - ffff["xyz"].usr)
    Luv[2] = 13.0 * Luv[0] * (vs - ffff["xyz"].vsr)


def convert_sRGB_XYZ(rgb=[], XYZ=[]):
    temp = [0, 0, 0]
    i = 0

    for i in range(3):
        if (rgb[i] <= 0.04045):
            temp[i] = rgb[i] / 12.92
        else:
            temp[i] = pow((rgb[i]+0.055)/1.055, 2.4)

    XYZ[0] = 0.4124*temp[0]+0.3576*temp[1]+0.1805*temp[2]
    XYZ[1] = 0.2126*temp[0]+0.7152*temp[1]+0.0722*temp[2]
    XYZ[2] = 0.0193*temp[0]+0.1192*temp[1]+0.9505*temp[2]


def image_blur(inn, out):
    m = 1./9
    x, y, ch = 0, 0, 0
    # for each row, column, and colour channel,
    for y in range(inn.height):
        for x in range(inn.width):
            summ = [0.0, 0.0, 0.0]
            for ch in range(3):
                summ[ch] = (
                    m * image_get_pixeld(inn, x-1, y-1, ch) +
                    m * image_get_pixeld(inn, x  , y-1, ch) +
                    m * image_get_pixeld(inn, x+1, y-1, ch) +
                    m * image_get_pixeld(inn, x-1, y  , ch) +
                    m * image_get_pixeld(inn, x  , y  , ch) +
                    m * image_get_pixeld(inn, x+1, y  , ch) +
                    m * image_get_pixeld(inn, x-1, y+1, ch) +
                    m * image_get_pixeld(inn, x  , y+1, ch) +
                    m * image_get_pixeld(inn, x+1, y+1, ch)
                )

            # if 250 < x < 256 and 250 < y < 256:
            #     print summ, RGB(summ[0]*255, summ[1]*255, summ[2]*255)

            image_set_pixel(out, x, y, RGB(summ[0]*255, summ[1]*255, summ[2]*255))

    # print out.data
    # raw_input()


def image_desaturate(inn):
    # use the gimp "luminance" algorithm.
    for y in range(inn.height):
        for x in range(inn.width):
            clr = image_get_pixel(inn, x, y)
            out = (0.3 * GetRValue(clr) + 0.59*GetGValue(clr) + 0.11*GetBValue(clr))

            if 250 < x < 256 and 250 < y < 256:
                print x, y, out, RGB(out, out, out)

            image_set_pixel(inn, x, y, RGB(out, out, out))


def main():
    import sys
    img_file = sys.argv[1]

    # DONE!
    img1 = image_load(img_file)

    print "image_load() DONE!"

    img2 = image_create(img1.width, img1.height)
    img3 = image_create(img1.width, img1.height)

    print len(img2.data), len(img3.data)

    print "image_create() DONE!"

    # try sobel method.
    image_blur(img1, img2)
    image_desaturate(img2)
    image_save(img2, "grayscale.png")

    print "img2.image_save DONE!"

    image_sobel(img2, img3)
    image_save(img3, "sobel-grays.png")

    print "img3.image_save DONE!"

    # try colour method
    image_blur(img1, img2)

    ts = time.time()
    print "start image_sobel_colour..."
    image_sobel_colour(img2, img3)
    print "done image_sobel_colour...", time.time() - ts

    image_save(img3, "sobel-colourdiff.png")
    return 0


if __name__ == "__main__":
    main()
