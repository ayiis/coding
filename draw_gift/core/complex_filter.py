import q
import random
import cv2 as cv
import numpy as np


class ComplexFilter:

    def light_mask_points(frame, points=None, light_size=42, distance_fix=1.0 / 5):
        """
            distance_fix: 光圈大小，基数是全图尺寸，到达极限大小时 亮度=0
            light_size: 光源大小，在此范围内亮度不衰减
            points:
                0个点 生成1个点在图片中央
                count个点 => 蒙版灰度 = SUM{count: 1/n * ((距离-light_size) / (distance_fix * 图片尺寸) )}
        """
        if points is None:
            # points = []
            # for i in range(random.randint(1, 4)):
            #     points.append((random.randint(0, height), random.randint(0, width)))
            # print("create random points:", points)
            points = [(frame.shape[0] // 2, frame.shape[1] // 2)]

        mask_frame = np.zeros((frame.shape[0], frame.shape[1]))

        height, width = mask_frame.shape
        distance = int(np.linalg.norm([height, width])) - 1
        distanced = distance * distance_fix
        print("distance_fix:", distance_fix)

        para = 1 / len(points) / distanced
        for x in range(height):
            for y in range(width):
                c = 1
                for point in np.array(points):
                    c *= (np.linalg.norm(point - [x, y]) - light_size) * para
                if c < 0:
                    c = 0
                mask_frame[x, y] = c

        mask_frame[mask_frame > 1] = 1
        mask_frame = 1 - mask_frame
        frame_lab = cv.cvtColor(frame, cv.COLOR_BGR2Lab).astype(np.double)
        frame_lab[:, :, 0] *= mask_frame
        frame_lab = frame_lab.astype(np.uint8)
        frame_cast = cv.cvtColor(frame_lab, cv.COLOR_Lab2BGR)

        return frame_cast

    def light_mask_line(frame, line=None, light_size=42, distance_fix=1.0 / 5):
        """
            line 传入2个点A和B，标示起始和结束
            方法：
                目标点为P，P在AB上的垂直线的点为C，计算PA、PB、PC的距离，取最小值dd
                (dd - light_size) / distanced 为亮度衰减幅度，达到1.0时亮度为最低
        """
        if line is None:
            line = np.array([[0, 0], [0, frame.shape[1]]])
        p1, p2 = line[:2]
        mask_frame = np.zeros((frame.shape[0], frame.shape[1]))
        distance = int(np.linalg.norm([frame.shape[0], frame.shape[1]])) - 1
        distanced = distance * distance_fix
        # distanced = distance
        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                p3 = np.array([x, y])
                d1 = np.linalg.norm(p1 - p3)
                d2 = np.linalg.norm(p2 - p3)
                d3 = np.linalg.norm(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)
                dd = min(d1, d2, d3)  # 最短距离
                mask_frame[x, y] = (dd - light_size) / distanced

        mask_frame[mask_frame > 1] = 1
        mask_frame[mask_frame < 0] = 0
        mask_frame = 1 - mask_frame
        frame_lab = cv.cvtColor(frame, cv.COLOR_BGR2Lab).astype(np.double)
        frame_lab[:, :, 0] *= mask_frame
        frame_lab = frame_lab.astype(np.uint8)
        frame_cast = cv.cvtColor(frame_lab, cv.COLOR_Lab2BGR)
        return frame_cast

    def color_mask(frame, point_src=None, color_light=None, color_background=None, weight=0.42):
        """
            底色 color_background
            1个亮点 point_src 颜色为 color_light，向四周衰减
        """
        height, width, _ = frame.shape
        if point_src is None:
            xo, yo = width, height
        else:
            xo, yo = point_src

        image = np.ndarray((height, width, 3))
        image[:, :] = color_light
        origin = np.array([yo, xo])
        center = np.array([image.shape[1] // 2, image.shape[0] // 2])

        sqrt_dist = lambda x, y: (x ** 2 + y ** 2) ** (1 / 2)

        distance = 0
        if origin[0] < center[0] and origin[1] < center[1]:
            distance = sqrt_dist(width - 1 - xo, height - 1 - yo)
        elif xo <= center[0] and center[1] < yo:
            distance = sqrt_dist(width - 1 - xo, yo)
        elif center[0] < xo and yo <= center[1]:
            distance = sqrt_dist(xo, height - 1 - yo)
        else:
            distance = sqrt_dist(xo, yo)

        weight_b = (color_background[0] - color_light[0]) / distance
        weight_g = (color_background[1] - color_light[1]) / distance
        weight_r = (color_background[2] - color_light[2]) / distance

        for i in range(width):
            for j in range(height):
                dist = sqrt_dist(i - xo, j - yo)
                image[j, i] += [weight_b * dist, weight_g * dist, weight_r * dist]

        image = image.astype(np.uint8)
        blend = cv.addWeighted(frame, 1.0, image, weight, 0.0)
        # return image
        return blend

    def mosaic_mask(frame, point_a, point_b, neighbor=9):
        """
            马赛克的实现原理是把图像上某个像素点一定范围邻域内的所有点用邻域内左上像素点的颜色代替
            这样可以模糊细节，但是可以保留大体的轮廓
            :param int neighbor:  马赛克每一块的宽
        """
        x1, y1 = point_a
        x2, y2 = point_b
        for i in range(0, y2 - y1 - neighbor, neighbor):  # 关键点0 减去neighbor 防止溢出
            for j in range(0, x2 - x1 - neighbor, neighbor):
                rect = [j + x1, i + y1, neighbor, neighbor]
                color = frame[i + y1][j + x1].tolist()  # 关键点1的颜色
                left_up = (rect[0], rect[1])
                right_down = (rect[0] + neighbor - 1, rect[1] + neighbor - 1)  # 关键点2 减去一个像素
                cv.rectangle(frame, left_up, right_down, color, -1)

        return frame
