#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
归并排序，O(n log n)
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


target = [1,6,8,9,4,5,2,1,3,7,5,-5,-2,55,33,44,99,-9]

print target
print sorted(target)


def guibing(final_list, item):
    dlen = len(item)
    if dlen == 1:
        return final_list.append(item[0])
    hlen = dlen / 2

    left_list = []
    right_list = []

    # 左右数组各处理一半
    guibing(left_list, item[:hlen])
    guibing(right_list, item[hlen:])

    left_list_index, left_list_lenth = 0, len(left_list)
    right_list_index, right_list_length = 0, len(right_list)

    # 比较左右数组中的第index个元素，并将较小的元素放到 结果数组中
    while left_list_index < left_list_lenth and right_list_index < right_list_length:
        if left_list[left_list_index] < right_list[right_list_index]:
            final_list.append(left_list[left_list_index])
            left_list_index = left_list_index +1
        else:
            final_list.append(right_list[right_list_index])
            right_list_index = right_list_index +1

    # 将其余的元素放入 结果数组中
    final_list[:] = final_list + left_list[left_list_index:] + right_list[right_list_index:]


def main():
    final_list = []
    guibing(final_list, target)
    print "final_list:", final_list
    print sorted(target) == final_list


if __name__ == '__main__':
    main()
