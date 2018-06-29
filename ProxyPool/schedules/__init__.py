# coding=utf8

import tornado
import tornado.gen

import check_available
import check_unavailable
import check_fail
from proxy_crawler import validate

from proxy_crawler import (
    proxy_coderbusy_com,
    proxy_xicidaili_com,
    proxy_kuaidaili_com,
    proxy_66ip_cn,
    proxy_89ip_cn,
    proxy_ip3366_net,
    proxy_cn_proxy_com,
    proxy_us_proxy_org,
)

proxy_crawler_setting = {
    "proxy.coderbusy.com": proxy_coderbusy_com,
    "proxy.xicidaili.com": proxy_xicidaili_com,
    "proxy.kuaidaili.com": proxy_kuaidaili_com,
    "proxy.66ip.cn": proxy_66ip_cn,
    "proxy.89ip.cn": proxy_89ip_cn,
    "proxy.ip3366.net": proxy_ip3366_net,
    "proxy.cn-proxy.com": proxy_cn_proxy_com,
    "proxy.us-proxy.org": proxy_us_proxy_org,
}

from common import tornado_timmer
from proxy_crawler import config as crawler_config
import config as schedules_config


@tornado.gen.coroutine
def init(db):

    # check proxies pool periodically
    tornado_timmer.set_interval(schedules_config.setting["available_pool"]["period"], lambda: check_available.do(db))
    tornado_timmer.set_interval(schedules_config.setting["unavailable_pool"]["period"], lambda: check_unavailable.do(db))
    tornado_timmer.set_interval(schedules_config.setting["fail_pool"]["period"], lambda: check_fail.do(db))

    # init proxy crawler Job
    for proxy_crawler_name in proxy_crawler_setting:
        proxy_crawler_config = crawler_config.crawler_setting[proxy_crawler_name]
        if proxy_crawler_config["enable"]:

            print "Enable crawler job:", proxy_crawler_name

            # run in time of day
            if proxy_crawler_config.get("time_of_day"):
                tornado_timmer.set_clock(
                    proxy_crawler_config["time_of_day"],
                    lambda proxy_crawler_name=proxy_crawler_name: proxy_crawler_setting[proxy_crawler_name].do(db)
                )

            # run in the period
            elif proxy_crawler_config.get("period"):
                tornado_timmer.set_interval(
                    proxy_crawler_config["period"],
                    lambda proxy_crawler_name=proxy_crawler_name: proxy_crawler_setting[proxy_crawler_name].do(db)
                )
            else:
                print "No running plan for %s" % proxy_crawler_name
