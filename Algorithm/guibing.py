#!/usr/local/bin/python
#encoding:utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


target = [1,6,8,9,4,5,2,1,3,7,5,-5,-2,55,33,44,99,-9]

print target
print sorted(target)



def guibing(final_list, item):
    # print item
    dlen = len(item)
    if dlen == 1:
        return final_list.append(item[0])
    hlen = dlen / 2

    left_list = []
    right_list = []

    guibing(left_list, item[:hlen])
    guibing(right_list, item[hlen:])

    fl1, m_fl1 = 0, len(left_list)
    fl2, m_fl2 = 0, len(right_list)
    while fl1 < m_fl1 and fl2 < m_fl2:
        if left_list[fl1] < right_list[fl2]:
            final_list.append(left_list[fl1])
            fl1 = fl1 +1
        else:
            final_list.append(right_list[fl2])
            fl2 = fl2 +1
    final_list[:] = final_list + left_list[fl1:] + right_list[fl2:]
    # print left_list, "+" , right_list, "==>" , final_list[:]


def main():
    final_list = []
    guibing(final_list, target)
    print "final_list:", final_list
    print sorted(target) == final_list


if __name__ == '__main__':
    main()
