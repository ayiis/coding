"""
    实现 https://www.cnblogs.com/Anita9002/p/8691147.html
"""
import q
import time
import cv2 as cv
import numpy as np


class BasicFilter:

    def v1(frame, m_size=0.618):
        """
            羽化/虚化，以中央点为中心，向所有方向模糊，距离中点越远越虚化
            https://blog.csdn.net/yangtrees/article/details/9210153
        """
        heigh, width = frame.shape[:2]
        centerX, centerY = heigh // 2, width // 2
        maxV = centerX * centerX + centerY * centerY
        minV = maxV * (1 - m_size)

        def av_val(x):
            if x > 255:
                return 255
            elif x < 0:
                return 0
            else:
                return x

        diff = maxV - minV
        ratio = width > heigh and heigh / width or width / heigh

        img = np.copy(frame)
        dst = np.zeros_like(img)
        for y in range(heigh):
            for x in range(width):
                b, g, r = img[y, x]
                dx = centerX - x
                dy = centerY - y

                if width > heigh:
                    dx = (dx * ratio)
                else:
                    dy = (dy * ratio)

                v = ((dx * dx + dy * dy) / diff) * 255

                dst[y, x] = [av_val(b + v), av_val(g + v), av_val(r + v)]

        return dst
