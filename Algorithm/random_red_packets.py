# -*- coding: utf-8 -*-
import random

total = 100
packets = 10

# 100个长度取10个点，排序 用sample，使每次取值都不一样
rlist = random.sample(range(total), packets)
rlist = sorted(rlist)

# 计算10个点的差值视为距离，最后一个点与第一个点的差值（负值）需要加100
result = [(rlist[i] - rlist[i - 1]) for i in range(packets)]
result[0] += total

# 10段距离加起来是100，距离即为红包的值
print(sum(result), result)


################################################

import pandas
import matplotlib.pyplot as plt

datarows = []
for i in range(10000):
    rlist = random.sample(range(total), packets)
    rlist = sorted(rlist)
    result = [(rlist[i] - rlist[i - 1]) for i in range(packets)]
    result[0] += total
    datarows += result

pandas.DataFrame(datarows).hist(bins=256)
plt.show()
