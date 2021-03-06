"""
    实现 https://www.jianshu.com/p/c0759e322de7
"""
import q
import time
import cv2 as cv
import numpy as np


class FilterR:

    def channel_b(frame):
        frame_cast = np.zeros(frame.shape)
        frame_cast[:, :, 0] = frame[:, :, 0]
        return frame_cast

    def channel_g(frame):
        frame_cast = np.zeros(frame.shape)
        frame_cast[:, :, 1] = frame[:, :, 1]
        return frame_cast

    def channel_r(frame):
        frame_cast = np.zeros(frame.shape)
        frame_cast[:, :, 2] = frame[:, :, 2]
        return frame_cast

    def gray_hsv(frame):
        """
            灰度化滤镜 hsv
        """
        hsv_gray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)[:, :, 2]
        return cv.cvtColor(hsv_gray, cv.COLOR_GRAY2BGR)

    def gray_lab(frame):
        """
            灰度化滤镜 lab
        """
        lab_gray = cv.cvtColor(frame, cv.COLOR_BGR2Lab)[:, :, 0]
        return cv.cvtColor(lab_gray, cv.COLOR_GRAY2BGR)

    def gray_bgr(frame):
        """
            灰度化滤镜 bgr
        """
        bgr_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        return cv.cvtColor(bgr_gray, cv.COLOR_GRAY2BGR)

    def gray_bgr_mean(frame):
        """
            灰度化滤镜 bgr 均值
        """
        bgr_mean_gray = np.mean(frame, axis=2)
        return cv.cvtColor(bgr_mean_gray.astype(np.uint8), cv.COLOR_GRAY2BGR)

    def gray_bgr_fix(frame):
        """
            灰度化滤镜 bgr 加权平均
        """
        b, g, r = frame[:, :, 0], frame[:, :, 1], frame[:, :, 2]
        frame_cast = 0.11 * b + 0.59 * g + 0.30 * r
        return cv.cvtColor(frame_cast.astype(np.uint8), cv.COLOR_GRAY2BGR)

    def reversal(frame):
        """
            反色滤镜
        """
        return 255 - frame

    def bin(frame):
        """
            黑白滤镜 (自适应)
        """
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)[:, :, 2]
        # return cv.threshold(frame_gray, 128, 255, cv.THRESH_BINARY)[1]
        return cv.adaptiveThreshold(frame_gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 5, 10)

    def noncolor(frame):
        """
            去色滤镜 https://mangoroom.cn/opencv/remove-color-filter.html
        """
        frame_cast = frame.astype(np.int32)
        frame_cast = (np.min(frame_cast, axis=2) + np.max(frame_cast, axis=2)) // 2
        return frame_cast.astype(np.uint8)

    def casting(frame):
        """
            熔铸滤镜 https://mangoroom.cn/opencv/casting-filter.html
        """
        frame_cast = frame.astype(np.int32)
        b, g, r = frame_cast[:, :, 0].copy(), frame_cast[:, :, 1].copy(), frame_cast[:, :, 2].copy()
        frame_cast[:, :, 0] = 128 * b / (g + r + 1)
        frame_cast[:, :, 1] = 128 * g / (b + r + 1)
        frame_cast[:, :, 2] = 128 * r / (b + g + 1)
        frame_cast[frame_cast < 0] = 0
        frame_cast[frame_cast > 255] = 255
        return frame_cast.astype(np.uint8)

    def frozen(frame):
        """
            冰冻滤镜 https://mangoroom.cn/opencv/frozen-filter.html
        """
        frame_cast = frame.astype(np.int32)
        # b, g, r = frame_cast[:, :, 0], frame_cast[:, :, 1], frame_cast[:, :, 2]
        b, g, r = frame_cast[:, :, 0].copy(), frame_cast[:, :, 1].copy(), frame_cast[:, :, 2].copy()
        frame_cast[:, :, 0] = abs(b - g - r) * 3 >> 2
        frame_cast[:, :, 1] = abs(g - b - r) * 3 >> 2
        frame_cast[:, :, 2] = abs(r - b - g) * 3 >> 2
        frame_cast[frame_cast < 0] = 0
        frame_cast[frame_cast > 255] = 255
        return frame_cast.astype(np.uint8)

    def blizzard(frame):
        """
            霜冻滤镜
        """
        frame_cast = frame.astype(np.double)
        b, g, r = frame_cast[:, :, 0], frame_cast[:, :, 1], frame_cast[:, :, 2]
        frame_cast[:, :, 0] = abs(b - g - r) * 3 / 4
        frame_cast[:, :, 1] = abs(g - b - r) * 3 / 4
        frame_cast[:, :, 2] = abs(r - b - g) * 3 / 4

        # frame_cast = frame.astype(np.double)
        # b, g, r = frame_cast[:, :, 0].copy(), frame_cast[:, :, 1].copy(), frame_cast[:, :, 2].copy()
        # frame_cast[:, :, 0] = abs(0.75 * b - 0.75 * g - 0.75 * r)
        # frame_cast[:, :, 1] = abs(1.3125 * g - 0.5625 * b - 0.1875 * r)
        # frame_cast[:, :, 2] = abs(1.046875 * r + 0.140625 * b + 0.421875 * g)

        # frame_cast[:, :, 0] = abs(b - g - r) * 0.75
        # frame_cast[:, :, 1] = abs(g - abs(b - g - r) * 0.75 - r) * 0.75
        # frame_cast[:, :, 2] = abs(r - abs(b - g - r) * 0.75 - abs(g - abs(b - g - r) * 0.75 - r) * 0.75) * 0.75

        frame_cast[frame_cast < 0] = 0
        frame_cast[frame_cast > 255] = 255
        return frame_cast.astype(np.uint8)

    def comic(frame):
        """
            连环画滤镜 https://mangoroom.cn/opencv/comic-filter.html
            要注意 opencv的赋值是引用的 需要使用 copy
        """
        frame_cast = frame.astype(np.double)
        b, g, r = frame_cast[:, :, 0].copy(), frame_cast[:, :, 1].copy(), frame_cast[:, :, 2].copy()
        frame_cast[:, :, 0] = abs(b - g + b + r) * g / 256  # B
        frame_cast[:, :, 1] = abs(b - g + b + r) * r / 256  # G
        frame_cast[:, :, 2] = abs(g - b + g + r) * r / 256  # R
        frame_cast[frame_cast < 0] = 0
        frame_cast[frame_cast > 255] = 255
        return frame_cast.astype(np.uint8)

    def sketch(frame):
        """
            素描滤镜 https://mangoroom.cn/opencv/drawing-filter.html
        """
        hsv_gray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)[:, :, 2]
        hsv_gray_re = 255 - hsv_gray
        hsv_gray_re = cv.GaussianBlur(hsv_gray_re, (7, 7), 0)

        hsv_gray = hsv_gray.astype(np.int32)
        hsv_gray_re = hsv_gray_re.astype(np.int32)

        frame_cast = hsv_gray + (hsv_gray * hsv_gray_re) / (255 - hsv_gray_re)

        frame_cast[frame_cast < 0] = 0
        frame_cast[frame_cast > 255] = 255
        return cv.cvtColor(frame_cast.astype(np.uint8), cv.COLOR_GRAY2BGR)

    def grave(frame, fix=1):
        """
            浮雕-1 雕刻1 滤镜 https://mangoroom.cn/opencv/relief-and-carving-filter.html
            fix 越大 阴影越大，立体感越强，浮雕-1 雕刻1
        """
        fix_abs = abs(fix)
        fix = fix < 0 and -1 or 1
        frame_cast = frame.astype(np.int32)

        frame_cast1 = frame_cast[:-fix_abs, :-fix_abs]
        frame_cast2 = frame_cast[fix_abs:, fix_abs:]
        frame_cast = fix * (frame_cast2 - frame_cast1) + 128

        frame_cast[frame_cast < 0] = 0
        frame_cast[frame_cast > 255] = 255

        # return frame_cast.astype(np.uint8)  # 有彩色阴影

        frame_cast = cv.cvtColor(frame_cast.astype(np.uint8), cv.COLOR_BGR2HSV)[:, :, 2]
        return cv.cvtColor(frame_cast, cv.COLOR_GRAY2BGR)

    def carving(frame):
        """
            浮雕-1 雕刻1 https://blog.csdn.net/yangtrees/article/details/9090607
        """
        return FilterR.carving(frame, -1)

    def vintage(frame):
        """
            老旧照片滤镜 https://mangoroom.cn/opencv/vintage-filter.html
        """
        frame_cast = frame.astype(np.int32)
        b, g, r = frame_cast[:, :, 0].copy(), frame_cast[:, :, 1].copy(), frame_cast[:, :, 2].copy()
        frame_cast[:, :, 0] = 0.272 * r + 0.534 * g + 0.131 * b
        frame_cast[:, :, 1] = 0.349 * r + 0.686 * g + 0.168 * b
        frame_cast[:, :, 2] = 0.393 * r + 0.769 * g + 0.189 * b
        frame_cast[frame_cast < 0] = 0
        frame_cast[frame_cast > 255] = 255
        return frame_cast.astype(np.uint8)

    def vignetting(frame):
        """
            晕影vignetting滤镜 https://mangoroom.cn/opencv/create-vignetting-filter-in-opencv.html
        """
        # frame_cast = frame.astype(np.double)
        # frame = frame.astype(np.double)
        frame_gradient1 = cv.imread("./tests/gradient.png", 0)
        frame_gradient2 = frame_gradient1.astype(np.double)
        # frame_gradient2 = frame_gradient2 / 255
        frame_gradient2 = cv.normalize(frame_gradient2, None, alpha=0.46, beta=1.00, norm_type=cv.NORM_MINMAX)
        frame_gradient3 = cv.resize(frame_gradient2, (frame.shape[1], frame.shape[0]))
        for x in range(frame_gradient3.shape[0]):
            for y in range(frame_gradient3.shape[1]):
                if x % 100 ==0 and y % 100 ==0:
                    print(frame_gradient3[x, y], frame_gradient3[x, y] / 255)

        frame_gradient_mask = frame_gradient3
        # frame_gradient_mask = cv.normalize(frame_gradient3, 0, 255, 32)
        a = frame_gradient_mask[frame_gradient_mask!=0]
        print(a.shape)
        b = a[a != 1]
        print(b.shape)

        # q.d()
        frame_lab = cv.cvtColor(frame, cv.COLOR_BGR2Lab).astype(np.double)
        # frame_lab = frame_lab.astype(np.double)
        # frame_lab = frame_gradient_mask * frame_lab1[:, :, 0]
        # q.d()
        frame_lab[:, :, 0] *= frame_gradient_mask
        # frame_lab[frame_lab>255] = 255
        # frame_lab[frame_lab<0] = 0
        frame_lab = frame_lab.astype(np.uint8)
        frame_cast = cv.cvtColor(frame_lab, cv.COLOR_Lab2BGR)
        return frame_cast

    def draw_oil(frame):
        # do edge detection on a grayscale image
        gray = cv.cvtColor(frame, cv.COLOR_BGRA2GRAY)
        gray = cv.blur(gray, (3, 3))  # this blur gets rid of some noise
        edges = cv.Canny(gray, 50, 150, apertureSize=3)  # this is the edge detection

        # the edges are a bit thin, this blur and threshold make them a bit fatter
        kernel = np.ones((3, 3), dtype=np.float) / 12.0
        edges = cv.filter2D(edges, 0, kernel)
        edges = cv.threshold(edges, 50, 255, 0)[1]

        # and back to colour...
        edges = cv.cvtColor(edges, cv.COLOR_GRAY2BGR)

        # this is the expensive operation, it blurs things but keeps track of
        # colour boundaries or something, heck, just play with it
        shifted = cv.pyrMeanShiftFiltering(frame, 5, 20)

        # now compose with the edges, the edges are white so take them away
        # to leave black
        return cv.subtract(shifted, edges)

