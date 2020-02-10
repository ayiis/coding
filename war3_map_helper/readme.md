
## Jass.sublime-package

    Sublime Text的染色插件
    里面的文件被打包成zip，然后放置在packages目录即可被sublime自动加载


## 可调用的翻译接口

    ✅ 百度翻译

        - 每月免费 200w 字符，目前1张地图使用了 15w

        - 翻译质量较差

    ✅ 谷歌翻译

        - 网页端，支持文档翻译

        - 质量较好

        - 使用 pupeerteer 自动翻译


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
            CustomDefeatBJ
            DialogSetMessageBJ
            MultiboardSetItemValueBJ

        SKIP:
            ✅ ^TRIGSTR_[\d]+$

            ✅ *注意，字符串可跨行

            ✅ unit.ini 的跨行问题

            ✅ mapskin.txt 并没有汉化所有字符串

            ✅ war3map.j 方法名orc被汉化了

                ✅ 这种网址可如何是好啊？
                    
                    ==> https://wintermaul.one/

                平常的赋值很难汉化到

                    set udg_HINT[1]=(udg_HINT[0]+"Visit |cff00FF00ENT|r forum for see news, changelogs, bug reports, suggestions, etc. |cff00FF00https://www.entgaming.net|r")

                    call DisplayTimedTextToPlayer(loc_player01,0,0,10,"-disable - Disables reacts made by -reg")
                    -disable

            ✅ 没有lni 转换出来 《光束爆破, 警察菜刀》 的 模型丢了。。。

                光束爆破: "war3mapImported\\Magic Orb.mdl"
                警察菜刀: "war3mapImported\\GyroCopter.mdl"

                自带的(listfile) 和火龙分析结果 都不靠谱

                - 先转出来 lni

                - 通过提取所有字符串获得所有资源路径

                - 填入 (listfile)

                - 替换原来的 (listfile)

                - 重新转出来

            ✅ 这种自定义路径的 | 替换到魔兽目录的资源 (是自带的，忽略)

                file = "Abilities\\Spells\\Orc\\Purge\\PurgeBuffTarget.mdl"


    ⏱ BUG:

        trigstr 被提取 到了 字典里
        翻译结果前后不一致，不同类型的脚本间有差异:

            释义 错误: (选择了不恰当的释义)（与熟知的释义不符）（多见于游戏）

                - сундуке 会被翻译成 胸围
                - перезарядка => 冷却
                - время действия => 持续时间
                - босс => boss

            名词前后不一致: (变形太多)

                - город
                - райдне => 赖德(Raidne)
                - халген => 海尔根(Halgen)
                - лигос => 利格斯(Ligos)
                - чейдинхолом => 启顿霍林(Cheydinhol)
                - аквилея => 阿奎莱亚(Aquileia)
                - ансельвуд => 安塞尔伍德(Anselwood)
                - заргос => 萨尔戈斯(Zargos)
                - города => 布鲁日(Brugge)
                - берхольн => 伯克霍尔(Berkholn)
                - кингланда => 王国领地(Kingland)
                - нордлингским => 诺德(Nordling)
                - аскарии => 阿斯卡里亚(Ascaria)
                - кроуг => 克罗格(Kroog)
                - винсхил => 温斯希尔(Winshill)
                - салем => 塞勒姆(Salem)
                - норвинг => 挪威(Norving)
                - игвар => 伊格瓦尔(igvar)
                - дрим => 梦(Dream)
                - ангорведа => 安哥维达(Angorveda)
                - архилич => 扎蒙(Zeymon)
                - анифуса => 阿尼法斯(Anifus)
                - альбрехт => 阿尔布雷希特(Albrecht)
                - холти => 霍尔蒂(Holty)
                - магнус => 马格努斯(Magnus)
                - арантира => 阿兰蒂拉(Arantira)
                - Валенват => 瓦伦瓦(Valenvate)
                - Волхириан => 沃尔克希尔(Volhirian)
                - элвине верентисе => 阿尔文·韦尔尼斯(Alvin Verntis)
                - верентис => 韦尔尼斯(Verntis)
                - Мирвуд => 米尔伍德(Mirwood)
                - Кронли => 克朗利(Cronley)
                - Аквилейский => 阿基林(Aquilean)
                - Хамдия => 哈米迪亚(Hamdia)
                - Хавмер => 霍默(Hawmer)
                - клабище => 杜什尼克(Dushnik)
                - Глубины Ортала => 深邃的奥尔塔拉(Orthal)
                - валтрум => 瓦尔特鲁姆(Valtrum)
                - реинов => 雷诺夫(Reinov)
                - гранстранг => 格兰斯特朗(Granstrang)
                - аркани => 拉索(Lasso)
                - Аурэль => 奥雷尔(Aurel)


        jass的 漂浮文字 的地名都集中在 Trig_Loki_Actions ？


# 战役地图汉化方法

    1. 火龙重写 listfile

    2. w3x2lni 解压成 lni

    3. 在map文件夹里面把所有章节的 w3x 汉化

        - 删除最外层 w3n 的 war3mapskin.txt 文件的自定义字体
        - 删除所有 w3x 的 war3mapskin.txt 文件的自定义字体

    4. 在火龙里面直接替换 w3x

    5. 最外层的 w3n 需要先 w3x2lni 打包成 w3x 再替换资源

        对应关系：

            - war3mapskin.txt -> war3mapskin.txt
            - war3campaign.wts -> war3campaign.wts

# 注意事项

    搜索 #!!!!

    1. worker.py 开启/关闭 wts 翻译跳过空格



python map_analyzer.py

python translation_tool.py

cd lib

python t_pyppeteer.py

cp /tmp/up/base.en-zh.txt /mine/github/coding/war3_map_helper/data/

[  CHECK AND RENAME  ]

cd ..

rm Wintermaul_One_Revolution_v1.3 -rf && cp -r Wintermaul_One_Revolution_v1.3.bak Wintermaul_One_Revolution_v1.3
rm OpenHero_0_99j_ENG -rf && cp -r OpenHero_0_99j_ENG.bak OpenHero_0_99j_ENG
rm "PatisauR's ORPG 1" -rf && cp -r "PatisauR's ORPG 1.bak" "PatisauR's ORPG 1"
rm "Justice of Shadow 1.0" -rf && cp -r "Justice of Shadow 1.0.bak" "Justice of Shadow 1.0"
rm "Otro Mapa TD de Warcraft III" -rf && cp -r "Otro Mapa TD de Warcraft III.bak" "Otro Mapa TD de Warcraft III"
rm "Schizophrenia 1.23.10" -rf && cp -r "Schizophrenia 1.23.10.bak" "Schizophrenia 1.23.10"
rm "ArtededefensaV4.7" -rf && cp -r "ArtededefensaV4.7.bak" "ArtededefensaV4.7"
rm "opt-The Black Road v1.2" -rf && cp -r "opt-The Black Road v1.2.bak" "opt-The Black Road v1.2"
rm "Daemonic Sword ORPG 6.79" -rf && cp -r "Daemonic Sword ORPG 6.79.bak" "Daemonic Sword ORPG 6.79"
rm "The-Chosen-Ones-1.0_x" -rf && cp -r "The-Chosen-Ones-1.0_x.bak" "The-Chosen-Ones-1.0_x"
rm "Paranormal_Underworld_ORPG_Final_L" -rf && cp -r "Paranormal_Underworld_ORPG_Final_L.bak" "Paranormal_Underworld_ORPG_Final_L"


python map_analyzer.py



```code

进度：

    ✅. fomatter 已经修复
    ⏱. 改造 TranslateWorkerForJ

```


``` 待处理

call DisplayTimedTextToForce(bj_FORCE_ALL_PLAYERS, 5., ("|c00ff0303最多 " +(I2S(udg_TempInteger4) + " potions of this kind can be held at the same time.")))
call DisplayTimedTextToForce(bj_FORCE_ALL_PLAYERS, 9., ((udg_Interlude_Colors[1] + "黑头巾的男人: ") +(udg_Interlude_Colors[2] + "Money... That is what matters in the end of the day for me. Hand over the money, if you will.")))
call DisplayTimedTextToForce(bj_FORCE_ALL_PLAYERS, 38., ((udg_Interlude_Colors[1] + "黑头巾的男人: ") +(udg_Interlude_Colors[2] + "The job is done... Phodom's family is dead.")))
call QuestSetTitle(udg_Optional_Q_5, "|c00FEBA0EOgre Dungeon")

```



我对地图做了2点改动：
1. 开放单机模式
2. 去除反作弊模块



``` 巨大的BUG

    w3x2lni 解压出来是重新构建了 wts 的
    所以必须，重新用 w3x2lni 打包！！！

    已确认:
        j
        wts

    如果只有任务(j)用到 wts 的时候，打包的时候 wts 文件就不见了？？？？？？

    还是直接用火龙解压吧。。。。。。

    w3n - the chosen one
        wts 有些字符串被用来命名了，不能翻译成中文，否则会死
        - 如果名称字符串也写到了 wts 里，那么遇到 没有空格的 不翻译

```
