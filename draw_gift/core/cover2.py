import q
import cv2 as cv
import numpy as np


class Cover2:
    """
        https://blog.csdn.net/yangtrees/article/details/9207051
    """

    def v1(frame_a, frame_b):
        """
            正片叠底模式
        """
        frame_c = frame_a * frame_b / 255
        return frame_c

    def v2(frame_a, frame_b):
        """
            屏幕/滤色 模式
        """
        frame_c = frame_b + frame_a * (1 - frame_b / 255)
        return frame_c

    def v3(frame_a, frame_b):
        """
            叠加 模式
        """
        frame_c = frame_b + (frame_a - 127.5) * (1 - abs(frame_b - 127.5) / 127.5)
        return frame_c

    def v4(frame_a, frame_b):
        """
            柔光 模式
        """
        frame_c = np.zeros_like(frame_a)
        a1 = np.where(frame_a >= 127.5)
        a2 = np.where(frame_a < 127.5)
        frame_a1 = frame_a[a1]
        frame_b1 = frame_b[a1]
        frame_c[a1] = frame_b1 + (255 - frame_b1) * (frame_a1 - 127.5) / 127.5 * (0.5 - abs(frame_b1 - 127.5) / 255)

        frame_a2 = frame_a[a2]
        frame_b2 = frame_b[a2]
        frame_c[a2] = frame_b2 - frame_b2 * (127.5 - frame_a2) / 127.5 * (0.5 - abs(frame_b2 - 127.5) / 255)

        return frame_c

    def v5(frame_a, frame_b):
        """
            强光 模式
        """
        frame_c = np.zeros_like(frame_a)
        a1 = np.where(frame_a >= 127.5)
        a2 = np.where(frame_a < 127.5)
        frame_a1 = frame_a[a1]
        frame_b1 = frame_b[a1]
        frame_c[a1] = frame_b1 + (255 - frame_b1) * (frame_a1 - 127.5) / 127.5

        frame_a2 = frame_a[a2]
        frame_b2 = frame_b[a2]
        frame_c[a2] = frame_b2 - frame_b2 * (127.5 - frame_a2) / 127.5

        return frame_c

    def v6(frame_a, frame_b):
        """
            颜色减淡 模式
        """

        frame_c = frame_b + frame_a * frame_b * (frame_b ** (1 / 3)) / (3 * 127.5)
        frame_c[frame_c > 255] = 255
        # q.d()
        return frame_c

    def v7(frame_a, frame_b):
        """
            颜色加深 模式 （未实现）
        """
        raise Exception("nothing here")

    def v8(frame_a, frame_b):
        """
            变亮 模式
        """
        frame_c = np.zeros_like(frame_a)
        cond = np.where(frame_a > frame_b)
        cond2 = np.where(frame_a <= frame_b)
        frame_c[cond] = frame_a[cond]
        frame_c[cond2] = frame_b[cond2]

        return frame_c

    def v9(frame_a, frame_b):
        """
            变暗 模式
        """
        frame_c = np.zeros_like(frame_a)
        cond = np.where(frame_a < frame_b)
        cond2 = np.where(frame_a >= frame_b)
        frame_c[cond] = frame_a[cond]
        frame_c[cond2] = frame_b[cond2]

        return frame_c

    def v10(frame_a, frame_b):
        """
            差值 模式
        """
        frame_c = abs(frame_a - frame_b)

        return frame_c

    def v11(frame_a, frame_b):
        """
            排除 模式
        """
        frame_c = frame_a + frame_b - frame_a * frame_b / 127.5

        return frame_c

    def v12(frame_a, frame_b):
        """
            差值 模式 (改)
        """
        frame_c = frame_a - frame_b
        q.d()
        frame_c[frame_c < 0] = 127 + frame_c[frame_c < 0]

        return frame_c
