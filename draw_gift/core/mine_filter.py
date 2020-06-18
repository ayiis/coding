"""
    自我实现
"""
import q
import time
import cv2 as cv
import numpy as np


class FilterM:

    def brighter(frame):
        frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        frame_hsv[:, :, 2] = cv.normalize(frame_hsv[:, :, 2], None, alpha=64, beta=255, norm_type=cv.NORM_MINMAX)
        frame_res = cv.cvtColor(frame_hsv, cv.COLOR_HSV2BGR)

        return frame_res

    def grinding(frame, key_rate=0.125):
        pass

    def obscure(frame, key_rate=0.125):

        frame_small = cv.resize(frame, (int(frame.shape[1] * key_rate), int(frame.shape[0] * key_rate)))
        frame_nor = cv.resize(frame_small, (frame.shape[1], frame.shape[0]))

        return frame_nor

    def tempo_star_night(frame):
        """
            思路1:
                - 缩放25%
                - 缩放400%
                - 颜色选 HSV 增加亮度锐化
                - 叠加到原图



            cv.imwrite("tmp.png", frame_small)
            cv.imwrite("tmp.png", frame_nor)
            cv.imwrite("tmp.png", frame_hsv)
        """

        # frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)[:, :, 2]
        # return cv.threshold(frame_gray, 128, 255, cv.THRESH_BINARY)[1]

        key_rate = 1 / 5

        frame_small = cv.resize(frame, (int(frame.shape[1] * key_rate), int(frame.shape[0] * key_rate)))
        frame_nor = cv.resize(frame_small, (frame.shape[1], frame.shape[0]))

        frame_hsv = cv.cvtColor(frame_nor, cv.COLOR_BGR2HSV)
        frame_hsv[:, :, 2] = cv.normalize(frame_hsv[:, :, 2], None, alpha=64, beta=255, norm_type=cv.NORM_MINMAX)

        frame_res = cv.cvtColor(frame_hsv, cv.COLOR_HSV2BGR)

        cv.imwrite("tmp.png", frame_res)
        return frame_res
