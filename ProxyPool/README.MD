
proxy_source_site: {
    "https://duckduckgo.com",
    "https://tisocks.net/",
    "https://www.zoomeye.org/",
    "https://www.shodan.io/",
    "https://www.censys.io/",


    "https://leakedforums.com/threads/socks-proxy-list-06-08-2018-by-tisocks-net.2067/",
    "https://proxy.coderbusy.com/",
    "https://proxy.horocn.com/",
}


2 3 5 10 -- 5
10

(5*4+10) / 5 -- 6


table.available_pool

table.unavailable_pool

table.fail_pool

table.shit_pool


score: {
    "in use secceed": 2 / -2,
    "in cron1 secceed": 1 / -1,
    "in cron2 secceed": 0.75 / -0.75,
    "in cron3 secceed": 0.50 / -0.50,
    "in cron4 secceed": 0.25 / -0.25,

    "response every 10s -10% ": 0,
}

{
    "id",
    "proxy_ip",
    "proxy_port",
    "proxy_username",
    "proxy_password",

    "location",
    "delay",
    "create_datetime",
    "last_validate_datetime",

    "a_https": {
        0: "不支持",
        1: "支持",
    },
    "a_post": {
        0: "不支持",
        1: "支持",
    },

    "anoy": {
        0: "非匿名",
        1: "匿名",
        2: "高匿名",
    }
}

import urllib2,os; pf='Package Control.sublime-package'; ipp = sublime.installed_packages_path(); os.makedirs( ipp ) if not os.path.exists(ipp) else None; urllib2.install_opener( urllib2.build_opener( urllib2.ProxyHandler( ))); open( os.path.join( ipp, pf), 'wb' ).write( urllib2.urlopen( 'http://sublime.wbond.net/' +pf.replace( ' ','%20' )).read()); print( 'Please restart Sublime Text to finish installation')
cronjob {
    "cron1 60 * 20分钟": "检查可用IP池内的IP" / double_check / 60 * timeout / fail_to_save_to_cron2,

    "cron2 60 * 60 * 2小时": "检查暂时不可用IP池内的IP" / double_check / 60 * timeout / fail_to_save_to_cron3,

    "cron3 60 * 60 * 24 * 2天": "检查持续不可用IP池内的IP" / double_check / 60 * timeout,

    "cron4 60 * 60 * 24 * 20天": "检查废弃IP池内的IP" / double_check / 60 * timeout,
}

api {
    "get_a_proxy": ["id", "proxy_ip", "proxy_port", "proxy_username", "proxy_password", "anoy"],
    "free_a_proxy": ["id"],
    "free_a_proxy": ["id"],
}


