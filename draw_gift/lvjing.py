import q
import time
import cv2 as cv
import numpy as np
"""
cv.imread(raw_frame_name)
cv.imwrite("temp.jpg", test)
来吧 描线 边缘计算 再只提取边缘附近的色彩
"""

from core import basic_filter
from core.spec_filter import FilterR
from core.mine_filter import FilterM
from core.complex_filter import ComplexFilter
from core import filter_oil
from core import dnn_filters
from core.cover import Cover
from core.cover2 import Cover2


class LvJing:

    def suggest(frame, template_size, bucket_size, step):
        step = min(frame.shape[:2]) // 420 + 1
        template_size = step
        bucket_size = 3
        return template_size, bucket_size, step

    def draw_oil(frame, template_size=3, bucket_size=3, step=1, suggest=False):
        """
            将模版(template_size)里出现最多的像素（灰度区间(bucket_size)范围内）的均值赋值给 模版中央的(step*step)个像素
        """
        # 使用推荐配置
        if suggest:
            template_size, bucket_size, step = LvJing.suggest(frame, template_size, bucket_size, step)

        print("draw oil args:", frame.shape, template_size, bucket_size, step)
        return filter_oil.apply(frame, template_size, bucket_size, step)

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

    def draw_edge(frame, min_val=168, max_val=252):
        # 使用 HSV 颜色空间，提取第三个通道作为灰度
        hsv_gray = cv.cvtColor(frame.astype(np.uint8), cv.COLOR_BGR2HSV)[:, :, 2]
        # 提取边缘使用Canny过滤器: https://docs.opencv.org/trunk/da/d22/tutorial_py_canny.html
        # `NotEdge` < min_val < `MaybeEdge` < max_val < `SureEdge`
        return cv.Canny(hsv_gray, min_val, max_val)


class MyCombo:
    def gaudiness(frame):
        """
            增艳滤镜
        """
        brighter_frame = FilterM.brighter(frame)
        return Cover2.v5(frame, brighter_frame)

    def tempo_star_night(frame):
        pass

    def good_dream(frame):
        """
            美梦滤镜（盗梦空间最后一幕）
        """
        obscure_frame = FilterM.obscure(frame, key_rate=0.15)
        brighter_frame = FilterM.brighter(frame)
        return Cover2.v5(obscure_frame, brighter_frame)

    def grinding():
        pass

    def obscure(frame):
        """
            朦胧滤镜
        """
        brighter_frame1 = FilterM.obscure(frame, 1 / 4)
        frame1 = Cover2.v8(frame, brighter_frame1)
        brighter_frame2 = FilterM.obscure(frame, 1 / 8)
        frame2 = Cover2.v8(frame1, brighter_frame2)
        return frame2


def wrapper(clss):
    """
        将默认的 uint8 转成范围更大的 int16 以便计算
    """
    def _wrap(func):
        return lambda frame_a, frame_b: func(frame_a.astype(np.int32), frame_b.astype(np.int32)).astype(np.uint8)

    funcs = [a for a in dir(clss) if a[0] != "_"]
    for func_name in funcs:
        setattr(clss, func_name, _wrap(getattr(clss, func_name)))


class BasicTool(object):
    def zoom(frame, rate):
        return cv.resize(frame, (int(frame.shape[1] * rate), int(frame.shape[0] * rate)))

    def resize(frame, width, height):
        return cv.resize(frame, (int(height), int(width)))


def main():

    base_name = "gift.png"
    base_name = "frame.jpg"
    base_name = "me2.png"
    base_name = "cc2.png"

    raw_frame = cv.imread(base_name)
    print("raw_frame:", raw_frame.shape)

    # DEBUG = True
    DEBUG = False

    if DEBUG:
        ts = time.time()
        # oil_frame = LvJing.draw_oil(raw_frame, template_size=1, bucket_size=1, step=1)
        oil_frame = LvJing.draw_oil(raw_frame, suggest=True)
        cv.imwrite("%s.oil.png" % (base_name), oil_frame)
        print("oil duration:", time.time() - ts)

    frame_oil = cv.imread("%s.oil.png" % (base_name))
    for model in dnn_filters.models:
        ts = time.time()
        dnn_frame = LvJing.draw_dnn_models(raw_frame, model_name=model)
        cv.imwrite("%s.dnn.%s.png" % (base_name, model), dnn_frame)
        print("dnn %s duration:" % (model), time.time() - ts)

        # q.d()
        resss = Cover.apply(frame_oil, dnn_frame, method="v1", d=1 - 0.618)
        cv.imwrite("%s.oil.dnn.%s.png" % (base_name, model), resss)

        # ree = LvJing.draw_edge(frame_oil)
        # cv.imwrite("frame.edge.jpg", ree)


if __name__ == "__main__":
    # main()
    # # frame = cv.imread("me.png")
    # frame = cv.imread("cc.jpg")
    # frame = BasicTool.resize(frame, frame.shape[0]//2.6, frame.shape[1]//2.6)
    # cv.imwrite("cc2.png", frame)
    # exit()
    wrapper(Cover2)
    frame_a = cv.imread("me2.png.dnn.eccv16_starry_night.png")
    frame_b = cv.imread("me2.png")
    frame_b = cv.imread("fruit.jpg")
    # ddd = Cover2.v4(frame_a, frame_b)
    # ddd = FilterR.blizzard(frame_b)
    # frame_b2 = FilterM.tempo_star_night(frame_b)
    # ddd = Cover2.v5(frame_b, frame_b2)
    # ddd = MyCombo.gaudiness(frame_b)
    ddd = MyCombo.good_dream(frame_b)
    # ddd = ComplexFilter.light_mask_points(frame_b, points=[(0, 0), (0, frame_b.shape[1])], distance_fix=1.0 / 4)
    # ddd = ComplexFilter.light_mask_line(frame_b, distance_fix=1.0 / 2.6)
    # ddd = ComplexFilter.color_mask(frame_b, point_src=(frame_b.shape[1] // 2, frame_b.shape[0] // 2), color_light=(0, 120, 255), color_background=(255, 0, 120))
    # ddd = ComplexFilter.mosaic_mask(frame_b, point_a=(119, 50), point_b=(419, 300), neighbor=9)
    cv.imwrite("me2.ddd.png", ddd)

"""

2020-06-05 16:00
working on create_gif.py

"""
