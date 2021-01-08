# 功能

本程序用于自动汉化 魔兽争霸的地图文件，支持 .w3x 对战文件和 .w3n 战役文件

目前仍在活跃更新 魔兽争霸地图的网站为 [Epic War](https://www.epicwar.com/)，大部分地图都是 俄语和英语

本程序理论上支持任意语言的汉化（翻译接口默认通过 puppeteer 调用 谷歌翻译 网页版）

## 依赖

[w3x2lni](https://github.com/sumneko/w3x2lni), [YDWE](https://github.com/actboy168/YDWE), 火龙解压

## 翻译的目标文件列表

```

j:
✅ war3map.j:

wts:
✅ war3map.wts

txt:
✅ war3mapskin.txt

ini:
✅ ability.ini
✅ buff.ini
✅ destructable.ini
✅ doodad.ini
✅ imp.ini
✅ item.ini
✅ misc.ini
✅ unit.ini
✅ upgrade.ini
✅ w3i.ini

```

# 要注意的问题

⚠️ (listfile)

    自带的 (listfile) 和火龙分析结果 不完全靠谱，可以使用下面方法优化：
        - 先转出来 lni
        - 通过提取所有字符串获得所有资源路径
        - 填入 (listfile)
        - 替换原来的 (listfile)
        - 重新转出来

⚠️ wts 文件

    1. 汉化问题

        有些不规范的地图的wts文件，包含了 作为系统命令ID的 单个英文单词，汉化会丢失技能，但目前无法通过程序判断，需要设置跳过

            - 如果名称字符串也写到了 wts 里，那么遇到 没有空格的 不汉化

            - 在 worker.py 开启/关闭 wts 汉化跳过空格

            - 搜索 #!!!! 并注释

    2. 解压重新打包问题

        w3x2lni 解压出来是重新构建了 wts 的，所以重新打包必须也用 w3x2lni

            已确认: j，wts 都存在重构变量名的现象

        如果只有任务(j)用到 wts 的时候，打包的时候无法自动引入 wts 文件

        变量名需要转换成大写，如： trigstr_000 ==> TRIGSTR_000

    3. 建议还是直接用火龙解压

⚠️ wts 文件

    目前仅具备 基于正则匹配的词法分析 的能力
        对这样的字符串无能为力
            set a = "test string"
            call diaplayMsg(a)

## 其它事项


## Jass.sublime-package

Sublime Text的染色插件

里面的文件被打包成zip，然后放置在packages目录即可被sublime自动加载

## 翻译接口

✅ 百度翻译

    - 每月免费 200w 字符，目前1张地图使用了 15w

    - 翻译质量很差

✅ 谷歌翻译

    - 网页端，支持文档翻译

    - 质量较好

    - 使用 pyppeteer 自动翻译

        🚫 pyppeteer 已停止维护 需要升级 [pyppeteer2](https://github.com/pyppeteer/pyppeteer)

        🚫 pyppeteer2 的 issues 首页就有10个 BUG，暂时搁置升级


    - 词库默认用大众常用高频词库，无法指定为游戏词库，效果有待提高

    - 翻译结果前后不一致，变形的单词（特别是俄语）经常不能保持前后译意一致

# 使用

## 普通对战地图 w3x 汉化步骤

1. 火龙重写 (listfile)

2. w3x2lni 解压成 lni

3. 执行本脚本汉化 map 目录

## 战役地图 w3n 汉化步骤

1. 火龙重写 (listfile)

2. w3x2lni 解压成 lni

3. 在map文件夹里面把所有章节的 w3x 汉化

    - 删除最外层 w3n 的 war3mapskin.txt 文件的自定义字体
    - 删除所有 w3x 的 war3mapskin.txt 文件的自定义字体

4. 在火龙里面直接替换 w3x

5. 最外层的 w3n 需要先通过 w3x2lni 打包成 w3x 再替换资源

    对应关系：

        - war3mapskin.txt -> war3mapskin.txt
        - war3campaign.wts -> war3campaign.wts

## 脚本执行例子

```bash

# 提取需要翻译的字符串
python map_analyzer.py

mkdir /tmp/up
python translation_tool.py

# 获取翻译结果
cd lib
python t_pyppeteer.py
cp /tmp/up/base.en-zh.txt /mine/github/coding/war3_map_helper/data/

# [  CHECK AND RENAME  ]

cd ..

rm "HolyWar20200404v3" -rf && cp -r "HolyWar20200404v3.bak" "HolyWar20200404v3"

# 重新执行，替换需要翻译的字符串
python map_analyzer.py

```
