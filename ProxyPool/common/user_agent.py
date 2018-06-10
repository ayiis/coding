
browser_ua = {
    "chrome":[
        # 版本号是Chrome之后的数字
        "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13",
    ],
    "firefox":[
        # 版本号是Firefox之后的数字。
        # N: 表示无安全加密 　　I: 表示弱安全加密 　　U: 表示强安全加密     上面的U代表加密等级
        "Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12",
    ],
    "safari":[
        # 版本号是Version之后的数字
        "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13",
        "Mozilla/5.0 (iPhone; U; CPU like Mac OS X) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93 Safari/419.3",
        # iphone safria浏览器
        "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3",
    ],
    "opera": [
        # 版本号是靠近Opera的数字。
        "Opera/9.27 (Windows NT 5.2; U; zh-cn)",
        "Opera/8.0 (Macintosh; PPC Mac OS X; U; en)",
        "Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0 ",
        # 安卓 Opera浏览器
        "Opera/9.80 (Android 4.0.3; Linux; Opera Mobi/ADR-1210241554) Presto/2.11.355 Version/12.10",
    ]
    "ie":[
        # MSIE后面跟的数字为IE的版本号，如MSIE 8.0代表IE8, Windows NT 6.1 对应操作系统 windows 7
        # Windows NT 6.0 对应操作系统 windows vista 　
        # Windows NT 5.2 对应操作系统 windows 2003 　　
        # Windows NT 5.1 对应操作系统 windows xp 　　
        # Windows NT 5.0 对应操作系统 windows 2000
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 5.0; Windows NT)",
    ],
    "360":[
        # 360
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; 360SE)",
        # 360SE
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; 360SE)",
        # 360极速浏览器
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ;  QIHU 360EE)",
    ],
    "maxthon":[
        # 傲游浏览器
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; Maxthon/3.0)",
    ],

    "qq":[
        # 安卓 QQ浏览器
        "Mozilla/5.0 (Linux; U; Android 4.0.3; zh-cn; M032 Build/IML74K) AppleWebKit/533.1 (KHTML, like Gecko)Version/4.0 MQQBrowser/4.1 Mobile Safari/533.1",
        # iphone QQ浏览器
        "MQQBrowser/38 (iOS 4; U; CPU like Mac OS X; zh-cn)",
    ],
    "android":[
        # 安卓 原生浏览器
        "Mozilla/5.0 (Linux; U; Android 4.0.3; zh-cn; M032 Build/IML74K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    ],
    "uc":[
        # 安卓 UC浏览器
        "IUC(U;iOS 5.1.1;Zh-cn;320*480;)/UCWEB8.9.1.271/42/800",
    ],
}

# updated 20160510
spider_ua = {
    # 百度爬虫/ 2.0 / 百度图片 / baidu+Transcoder转码
    "baidu": [
        "Baiduspider+(+http://www.baidu.com/search/spider.htm)",
        "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
        "Baiduspider-image+(+http://www.baidu.com/search/spider.htm)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.8;baidu Transcoder) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729)",
    ],
    # google爬虫 * 3 / Google图片搜索
    "google": [
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Googlebot/2.1 (+http://www.google.com/bot.html)",
        "Googlebot/2.1 (+http://www.googlebot.com/bot.html)",
        "Googlebot-Image/1.0",
    ],
    # 雅虎中国/雅虎美国(英文)
    "yahoo": [
        "Mozilla/5.0 (compatible; Yahoo! Slurp China; http://misc.yahoo.com.cn/help.html)",
        "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    ],
    # 新浪爱问爬虫
    "sina": [
        "iaskspider/2.0(+http://iask.com/help/help_index.html)",
         "Mozilla/5.0 (compatible; iaskspider/1.0; MSIE 6.0)"
    ],
    # 搜狗网站/ 搜狗? / 搜狗图片
    "sogou": [
        "Sogou web spider/3.0(+http://www.sogou.com/docs/help/webmasters.htm#07)",
        "Sogou Push Spider/3.0(+http://www.sogou.com/docs/help/webmasters.htm#07)"
        "Sogou Pic Spider/3.0(+http://www.sogou.com/docs/help/webmasters.htm#07)"
    ],
    # 网易有道
    "yodao": [
        "Mozilla/5.0 (compatible; YodaoBot/1.0;http://www.yodao.com/help/webmaster/spider/;)",
        "Mozilla/5.0 (compatible; YoudaoBot/1.0; http://www.youdao.com/help/webmaster/spider/; )",
        "Mozilla/5.0 (compatible;YoudaoFeedFetcher/1.0;http://www.youdao.com/help/reader/faq/topic006/;1 subscribers;)",
    ],
    # 微软MSN爬虫
    "ms": [
        "msnbot/1.0 (+http://search.msn.com/msnbot.htm)",
        "msnbot-media/1.1 (+http://search.msn.com/msnbot.htm)",
    ],
    # 微软BING爬虫
    "bing": [
        "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    ],
    # 360搜索 / 360网站安全检测
    "360": [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0); 360Spider",
        "360spider(http://webscan.360.cn)",
    ],
    # 腾讯搜搜 / 搜搜图片
    "soso": [
        "Sosospider+(+http://help.soso.com/webspider.htm)",
        "Sosoimagespider+(+http://help.soso.com/soso-image-spider.htm)",
    ],
}
