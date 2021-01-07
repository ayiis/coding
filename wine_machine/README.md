
# 这个项目是什么？

信息收集 + 过滤器，提高使用者的购物决策的效果，“货比三家不吃亏，价看三次有实惠”

包含：

+ 京东商品价格监控
+ 网易考拉价格监控
+ 网易严选价格监控
+ 豆瓣租房小组新帖浏览

## 功能

### 商品价格展示（以京东为例）

![京东商品列表](https://raw.githubusercontent.com/ayiis/coding/master/wine_machine/1610004918175.jpg)

当前价格 + 当前活动 + 可领取的券 + 计算所有折扣和凑单后的最低价格 + 用户自定义的好价（微信通知） + 库存信息 + 商家信息

### 商品历史价格

![商品历史价格](https://raw.githubusercontent.com/ayiis/coding/master/wine_machine/1610004741446.jpg)

记录每一次历史价格变动，包括 优惠券+活动折扣 之后的最低价格，图表化展示

### 豆瓣租房

![豆瓣租房小组新帖](https://raw.githubusercontent.com/ayiis/coding/master/wine_machine/1610005026521.jpg)

收集豆瓣租房相关小组的租房/转租帖子，展示时过滤掉大部分 求租｜中介｜价格不匹配｜无关 帖子

### 自定义过滤规则

![豆瓣租房过滤规则](https://raw.githubusercontent.com/ayiis/coding/master/wine_machine/1610006608475.jpg)

支持 标题 + 作者 + 价格范围匹配




# 使用

环境要求：
```
MacOS / CentOS
python3.6+
mongodb
```

安装依赖：

`pip install -i https://pypi.ayiis.me/simple/ --no-deps --upgrade aytool`

`pip install -r requirements.txt`

启动：

`python app.py`
