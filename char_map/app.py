import q
import cv2
import numpy as np
from all_char import char_set

print("char_set:", char_set)
char_map = {}

minx, miny = 99, 99
maxx, maxy = 0, 0

for char in char_set:
    try:

        # frame = cv2.zeros_like(32, 32)
        frame = np.zeros((32, 32), np.int8)
        frame[frame != 1] = 1

        cv2.putText(frame, char, (8, 16), 1, 1.2, 0, 1, cv2.LINE_AA)

        assert len(frame[0][frame[0] != 1]) == 0
        assert len(frame[:, 0][frame[:, 0] != 1]) == 0
        assert len(frame[-1][frame[-1] != 1]) == 0
        assert len(frame[:, -1][frame[:, -1] != 1]) == 0

        char_map[char] = frame

        # q.d()
        zzz = np.where(frame != 1)

        if min(zzz[0]) < minx:
            minx = min(zzz[0])
        if maxx < max(zzz[0]):
            maxx = max(zzz[0])

        if min(zzz[1]) < miny:
            miny = min(zzz[1])
        if maxy < max(zzz[1]):
            maxy = max(zzz[1])

        # cv2.imshow("no name", frame)
        # cv2.imwrite("no_name.jpg", frame)

        # cv2.waitKey(-1)

        # q.d()
        # exit(1)
    except Exception:
        pass
        # q.d()

# print("minx, miny:", minx, miny)
# print("maxx, maxy:", maxx, maxy)

fixed_minx, fixed_miny = 0, 1
fixed_maxx, fixed_maxy = 0, -2

count_minx, count_miny = 0, 0
count_maxx, count_maxy = 0, 0

for char in char_map:
    char_map[char] = char_map[char][minx + fixed_minx:maxx + fixed_maxx + 1, miny + fixed_miny:maxy + fixed_maxy + 1]

    # print("char:", char, char_map[char].shape)
    # print(char_map[char])
    if (any(char_map[char][:, 0] == 0)):
        count_miny += 1
    if (any(char_map[char][:, -1] == 0)):
        count_maxy += 1
    if (any(char_map[char][0] == 0)):
        count_minx += 1
    if (any(char_map[char][-1] == 0)):
        count_maxx += 1

print("common shape is:", char_map[char].shape)
# print("count_minx, count_miny:", count_minx, count_miny)
# print("count_maxx, count_maxy:", count_maxx, count_maxy)

test_char = "f"
min_count = 17 * 12

for char in char_map:
    ccount = np.count_nonzero(char_map[test_char] ^ char_map[char])
    if ccount == 0:
        min_char = char
        min_count = 0
        break
    elif ccount < min_count:
        min_char = char
        min_count = 0

assert min_count == 0
assert min_char == test_char
print("pass test")
print("")

# for char in char_map:
#     # print("char:", char)
#     # q.d()
#     char_map[char][char_map[char] != 0] = 255
#     char_map[char] = cv2.resize(char_map[char], (5, 5))
#     char_map[char][char_map[char] != 255] = 1
#     char_map[char][char_map[char] == 255] = 0
#     # frame_cut = cv2.resize(frame_cut, FIXED_SHAPE)
#     # cv::resize(paras.target_image, paras.target_image, cv::Size(510, 490));

# q.d()
target_frame = cv2.imread("1.jpeg", 0)
# target_frame = cv2.resize(target_frame, (target_frame.shape[0] * 2, target_frame.shape[1] * 2))
cv2.imwrite("target_frame.jpg", target_frame)
mean_frame = cv2.adaptiveThreshold(target_frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 10)

print("mean_frame:", mean_frame.shape)
cv2.imwrite("mean_frame.jpg", mean_frame)

zero_mean_frame = np.zeros_like(mean_frame)
zero_mean_frame[zero_mean_frame != 1] = 1

# mean_frame[mean_frame == 0] = 1
# mean_frame[mean_frame == 255] = 0
mean_frame[mean_frame == 255] = 1

for x in range(0, mean_frame.shape[0] - 17, 17):
    for y in range(0, mean_frame.shape[1] - 12, 12):
        target_area_frame = mean_frame[x:x + 17, y:y + 12]
        min_char = " "
        min_count = 17 * 12
        for char in char_map:
            ccount = np.count_nonzero(target_area_frame ^ char_map[char])
            if ccount == 0:
                min_char = char
                min_count = 0
                break
            elif ccount < min_count:
                min_char = char
                min_count = ccount

        # print(ccount, min_char)
        # q.d()
        zero_mean_frame[x:x + 17, y:y + 12] = char_map[min_char]


zero_mean_frame[zero_mean_frame == 1] = 255
cv2.imwrite("zero_mean_frame.1.jpg", zero_mean_frame)

