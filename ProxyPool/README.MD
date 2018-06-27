
Special settings by Header
{
    "ay-auth": "username:timestamp:token"
    "ay-conf": "default"
}


proxy_source_site = {
    "https://duckduckgo.com",
    "https://tisocks.net/",
    "https://www.zoomeye.org/",
    "https://www.shodan.io/",
    "https://www.censys.io/",

    https://hide.me/en/proxy


    "https://proxy.coderbusy.com/",
    http://www.ip3366.net/free/?page=2
    "https://leakedforums.com/threads/socks-proxy-list-06-08-2018-by-tisocks-net.2067/",
    https://www.us-proxy.org/
    https://free-proxy-list.net/

    # OCR REQUIRED
    https://proxy.horocn.com/free-proxy.html
    https://proxy.horocn.com/api/proxies?order_id=Q2801603964049822446&num=10&format=text&line_separator=win

    http://cn-proxy.com/
    http://cn-proxy.com/archives/218

    http://www.gatherproxy.com/proxylist/country/?c=Singapore
    https://www.proxynova.com/proxy-server-list/country-sg/
    https://hidemy.name/en/proxy-list/
    http://spys.one/en/
    http://www.freeproxylists.net/zh/
    http://www.goubanjia.com/

}

/*

https://proxy.horocn.com/api-doc.html?order_id=Q2801603964049822446

220.163.19.202:34736
119.96.195.161:25020
61.130.231.40:45979
112.194.95.36:22395
117.27.111.156:19029
114.221.116.77:43496
222.189.246.117:16697
27.204.121.142:16973
14.118.160.206:19496
117.81.204.215:32662

*/


2 3 5 10 -- 5
10

(5*4+10) / 5 -- 6


table.available_pool

table.unavailable_pool

table.fail_pool


score = {
    "in use secceed": 2 / -2,
    "in cron1 secceed": 1 / -1,
    "in cron2 secceed": 0.75 / -0.75,
    "in cron3 secceed": 0.50 / -0.50,
    "in cron4 secceed": 0.25 / -0.25,

    "response every 10s -10% ": 0,
}

db_struct = {
    "id",
    "proxy_host",
    "proxy_port",
    "proxy_username",
    "proxy_password",

    "location",
    "delay",
    "create_datetime",
    "last_validate_datetime",

    "http_get": False,
    "https_get": False,
    "http_post": False,
    "https_post": False,

    "anoy": {
        0: "非匿名",
        1: "匿名",
        2: "高匿名",
    },

    "score": 100,
    "data_source": "www.baidu.com",

}

cronjob = {
    "cron1 60 * 15分钟": "检查可用IP池内的IP" / double_check / 60 * timeout / fail_to_save_to_cron2,

    "cron2 60 * 60 * 3小时": "检查暂时不可用IP池内的IP" / double_check / 60 * timeout / fail_to_save_to_cron3,

    "cron3 60 * 60 * 24 * 3天": "检查持续不可用IP池内的IP" / double_check / 60 * timeout,

}


api = {
    "get_a_proxy": {
        "req": [
            "system_id",    # which system is this request come form
            "expire_time",  # [exclusive mode used]: how long should this proxy be realeased for this system
            "anoy",         # anonymous level(equal & large than) of required proxy
        ],
        "res": [
            "id",
            "proxy_host",
            "proxy_port",
            "proxy_username",
            "proxy_password",
        ],
    },
    "feedback_a_proxy": {
        "req": [
            "id",
            "success",      # True or False
            "request_time", # Eg. 12s
        ],
        "res": True,
    },
}
