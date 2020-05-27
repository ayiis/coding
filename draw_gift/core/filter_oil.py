import cv2 as cv
import numpy as np


def apply(frame, templateSize=3, bucketSize=3, step=1):
    """
        https://blog.csdn.net/qq_40755643/article/details/84787204
            - 将模版(templateSize)里出现最多的像素（灰度区间(bucketSize)范围内）的均值赋值给 模版中央的(step*step)个像素

        templateSize: 模版尺寸templateSize*templateSize像素。越小，色块越小，越清晰
        bucketSize: 灰度区间的个数，光滑度。 越小，颜色过渡区域越大，画质越模糊
        step: 步长（每个模版作用于多少个元素），每1个模版的结果处理step*step像素。越小越平滑，锯齿越小，但处理时间越长
    """
    gray = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
    # 灰度图在桶中的所属分区
    level_gray = ((gray / 256) * bucketSize).astype(int)
    h, w = frame.shape[:2]

    oilImg = np.zeros(frame.shape, np.uint8)  # 用来存放过滤图像

    for i in range(0, h, step):

        top = max(i - templateSize, 0)
        bottom = i + templateSize + 1
        bottom = min(bottom, h - 1)

        for j in range(0, w, step):

            left = max(j - templateSize, 0)
            right = j + templateSize + 1
            right = min(right, w - 1)

            target_area = level_gray[top:bottom, left:right]
            target_frame_area = frame[top:bottom, left:right]

            # 找出像素最多的桶以及它的数量
            buckets = np.unique(target_area, return_counts=True)
            max_index = np.argmax(buckets[1])
            maxBucket, bucketCount = buckets[0][max_index], buckets[1][max_index]

            # 对像素最多的桶，求其桶中所有像素的三通道颜色均值
            bucketsMean1 = target_frame_area[target_area == maxBucket].sum(axis=0)
            bucketsMean = (bucketsMean1 / bucketCount).astype(int)  # 三通道颜色均值

            # 将 颜色均值 填充到油画图
            oilImg[i:i + step, j:j + step] = bucketsMean

    return oilImg
