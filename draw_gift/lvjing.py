import q
import time
import cv2 as cv
import numpy as np
"""
cv.imread(raw_frame_name)
cv.imwrite("temp.jpg", test)
来吧 描线 边缘计算 再只提取边缘附近的色彩
"""

from core import filter_oil
from core import dnn_filters


class LvJing(object):

    @staticmethod
    def draw_oil(frame, templateSize=3, bucketSize=3, step=1):
        """
            将模版(templateSize)里出现最多的像素（灰度区间(bucketSize)范围内）的均值赋值给 模版中央的(step*step)个像素
        """
        return filter_oil.apply(frame, templateSize, bucketSize, step)

    @staticmethod
    def draw_dnn_models(frame, model_name="eccv16_the_wave"):
        """
            使用已经训练好的模型：
                instance_norm_mosaic: 未明确 教堂彩绘白玻璃窗
                instance_norm_candy: 未明确 红黄暗重色
                instance_norm_the_scream: Edvard Munch《The Scream》
                instance_norm_feathers: 未明确 黄绿清新色
                instance_norm_la_muse: Picasso《LA MUSE》
                instance_norm_udnie: francis picabia《udnie》
                eccv16_starry_night: Vincent van Gogh《starry night》
                eccv16_la_muse: Picasso《LA MUSE》
                eccv16_composition_vii: Wassily Kandinsky《Composition VII, 1913》
                eccv16_the_wave: 葛饰北斋《神奈川冲浪里》
        """
        return dnn_filters.apply_model(frame, model_name)

    @staticmethod
    def draw_edge(frame):
        # 使用 HSV 颜色空间，提取第三个通道作为灰度
        hsv_gray = cv.cvtColor(frame.astype(np.uint8), cv.COLOR_BGR2HSV)[:, :, 2]
        # 提取边缘使用Canny过滤器: https://docs.opencv.org/trunk/da/d22/tutorial_py_canny.html
        return cv.Canny(hsv_gray, 192, 256)


class Cover(object):
    """
        A: 上面图层像素的色彩值（A=像素值/255）
        B: 下面图层像素的色彩值（B=像素值/255）
        C: 混合像素的色彩值（C=像素值/255）
        该公式也应用于层蒙板
    """
    @staticmethod
    def apply(frame_a, frame_b, method="v1", **args):
        func = getattr(Cover, method)
        return func(frame_a / 255, frame_b / 255) * 255

    @staticmethod
    def v1(frame_a, frame_b, d=0.618):
        """
            不透明模式 C = d*A + (1-d)*B
        """
        frame_c = d * frame_a + (1 - d) * frame_b
        return frame_c

    @staticmethod
    def v2(frame_a, frame_b):
        """
            正片叠底模式 C = A*B
        """
        frame_c = frame_a * frame_b
        return frame_c

    @staticmethod
    def v3(frame_a, frame_b):
        """
            颜色加深模式 C = 1 - (1-B)/A
        """
        frame_c = 1 - (1 - frame_b) / frame_a
        return frame_c

    @staticmethod
    def v4(frame_a, frame_b):
        """
            颜色减淡模式 C = B/(1-A)
        """
        frame_c = frame_b / (1 - frame_a)
        return frame_c


def main():
    # raw_frame_name = "frame.jpg"
    raw_frame_name = "%s.oil.jpg" % "frame.jpg"
    raw_frame = cv.imread(raw_frame_name)

    # ts = time.time()
    # res_frame = LvJing.draw_oil(raw_frame)
    # cv.imwrite("%s.oil.jpg" % (raw_frame_name), res_frame)
    # print("duration:", time.time() - ts)    # 3.06s

    # ts = time.time()
    # res_frame = LvJing.draw_dnn_models(raw_frame, model_name="instance_norm_mosaic")
    # cv.imwrite("%s.oil.dnn.jpg" % (raw_frame_name), res_frame)
    # print("duration:", time.time() - ts)    # 3.06s

    frame_a = cv.imread("frame.jpg.oil.jpg")
    frame_b = cv.imread("frame.jpg.oil.jpg.oil.dnn.jpg")
    resss = Cover.apply(frame_a, frame_b, method="v1")
    cv.imwrite("frame.jpg.oil.jpg.oil.dnn.rssss.jpg", resss)

    ree = LvJing.draw_edge(frame_a)
    cv.imwrite("frame.ree.192.jpg", ree)


if __name__ == "__main__":
    main()
