
## Jass.sublime-package

    Sublime Text的染色插件
    里面的文件被打包成zip，然后放置在packages目录即可被sublime自动加载


## 需要处理的脚本

    ⏱ war3map.wts

        结构 [ ? ]
            STRING 0~XX
            {
                xxxx
            }

    ⏱ war3mapskin.txt

        结构 [ini]


    ⏱ table:

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
        ⏱ w3i.ini

    ⏱ war3map.j:

        结构 [Jass]

        Jass的常用方法: 
            QuestMessageBJ
            CreateQuestBJ
            CreateTextTagLocBJ
            QuestSetDescriptionBJ
            DisplayTimedTextToForce
            DialogAddButtonBJ
            SetMapDescription
            
            *注意，字符串可能跨行
