#!/usr/local/bin/python
#encoding:utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
百钱买百鸡的问题算是一套非常经典的不定方程的问题，题目很简单：
公鸡5文钱一只，母鸡3文钱一只，小鸡一文钱3只，
用100文钱买一百只鸡，其中公鸡，母鸡，小鸡都必须要有，问公鸡，母鸡，小鸡要买多少只刚好凑足100文钱。
"""

# x*y*z>0
# 5x+3y+z/3 = 100

print """ version 1 """
"""
暴力枚举算法
"""

for x in xrange(1, 100/5 + 1, 1):
    for y in xrange(1, 100/3 + 1, 1):
        for z in xrange(1, 100 + 1, 1):
            if 5*x + 3*y + z/3.0 == 100 and x + y + z == 100:
                print "x, y, z:", x, y, z


print """ version 2 """
"""
结合一个条件 (x+y+z=100)，解出z 的枚举算法
"""

for x in xrange(1, 100/5 + 1, 1):
    for y in xrange(1, 100/3 + 1, 1):
        z = 100 - x - y
        if 5*x + 3*y + z/3.0 == 100:
            print "x, y, z:", x, y, z



print """ version 3 """
"""
结合两个条件 (x+y+z=100，5x+3y+z/3=100)，解出y，z 的枚举算法
"""

for x in xrange(1, 100/5 + 1, 1):
    x = x + 0.0
    y = (100 - 7*x) / 4.0
    z = (300 + 3*x) / 4.0

    if x.is_integer() and y.is_integer() and z.is_integer() and x > 0 and y > 0 and z > 0:
        print "x, y, z:", x, y, z


print """ version 4 """
"""
结合两个条件 (x+y+z=100，5x+3y+z/3=100)，解出y，z
代入 x=4k 解方程，再判断自然数k的范围 (0< k && 25-7k >0)
思路1：将浮点数换成整数计算
思路2：代入 x=4k 统一解方程？
"""

for k in xrange(1, 4, 1):
    x = 4.0*k
    y = 25 - 7.0*k
    z = 75 + 3.0*k

    print "x, y, z:", x, y, z


# x + y + z == 100
# 5*x + 3*y + z/3.0 == 100

# y = 100 - x - z

# 5*x + 3*(100 -x - z) + z/3 == 100
# 5x + 300 - 3x -3z +z/3 == 100
# 2x - 8z/3 + 200 == 0
# z = (3x + 300)/4

# y = 100 - x - (3x + 300) / 4
# 4y = 400 - 4x - 3x - 300
# 4y = 100 - 7x
# y = (100 - 7x)/4



# x, y, z: 3 20 77
# x, y, z: 4 18 78
# x, y, z: 7 13 80
# x, y, z: 8 11 81
# x, y, z: 11 6 83
# x, y, z: 12 4 84
