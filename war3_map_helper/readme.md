
## Jass.sublime-package

    Sublime Text的染色插件
    里面的文件被打包成zip，然后放置在packages目录即可被sublime自动加载


## 可调用的翻译接口

    ✅ 百度翻译

        - 每月免费 200w 字符，目前1张地图使用了 15w

        - 翻译质量较差

    ⏱ 谷歌翻译

        - 网页端，支持文档翻译

        - 质量较好


## 需要处理的脚本

    ✅ war3map.wts

        结构 [ ? ]
            STRING 0~XX
            {
                xxxx
            }

    ✅ war3mapskin.txt

        结构 [ini]


    ✅ table:

        结构 [ini]

        ✅ ability.ini
        ✅ buff.ini
        ✅ destructable.ini
        ✅ doodad.ini
        🚫 imp.ini
        ✅ item.ini
        🚫 misc.ini
        ✅ unit.ini
        ✅ upgrade.ini
        ✅ w3i.ini


    ✅ war3map.j:

        结构 [Jass]

        Jass的常用方法: 
            QuestMessageBJ
            CreateQuestBJ
            CreateTextTagLocBJ
            QuestSetDescriptionBJ
            DisplayTimedTextToForce
            DialogAddButtonBJ
            SetMapDescription
            SetMapName
            BJDebugMsg
            SetTextTagText

        SKIP:
            ^TRIGSTR_[\d]+$

            *注意，字符串可跨行


    ⏱ BUG:

        trigstr 被提取 到了 字典里

