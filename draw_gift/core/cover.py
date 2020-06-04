import q
import cv2 as cv
import numpy as np


class Cover:
    """
        A: 上面图层像素的色彩值（A=像素值/255）
        B: 下面图层像素的色彩值（B=像素值/255）
        C: 混合像素的色彩值（C=像素值/255）
        该公式也应用于层蒙板
    """
    def apply(frame_a, frame_b, method="v1", **args):
        func = getattr(Cover, method)
        return func(frame_a / 255, frame_b / 255, **args) * 255

    def v1(frame_a, frame_b, d=0.618):
        """
            不透明模式 C = d*A + (1-d)*B
        """
        frame_c = d * frame_a + (1 - d) * frame_b
        return frame_c

    def v2(frame_a, frame_b):
        """
            正片叠底模式 C = A*B
        """
        frame_c = frame_a * frame_b
        return frame_c

    def v3(frame_a, frame_b):
        """
            颜色加深模式 C = 1 - (1-B)/A
        """
        frame_c = 1 - (1 - frame_b) / frame_a
        return frame_c

    def v4(frame_a, frame_b):
        """
            颜色减淡模式 C = B/(1-A)
        """
        frame_c = frame_b / (1 - frame_a)
        return frame_c
