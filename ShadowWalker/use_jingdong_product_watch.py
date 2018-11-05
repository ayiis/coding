#!/usr/local/bin/python
#encoding:utf8
import datetime
import sys
import time
import random
import json
import requests
import re
reload(sys).setdefaultencoding("utf-8")

item_id = 4214058


def get_it(item_id):
    headers = {
        "Cookie": """shshshfpa=77b7b44e-599e-b82e-20e4-2e36e51430df-1540525919; __jda=122270672.15405259200011633605594.1540525920.1540525920.1540525920.1; __jdc=122270672; __jdv=122270672|direct|-|none|-|1540525920001; _gcl_au=1.1.287338218.1540525920; __jdu=15405259200011633605594; shshshfpb=1f0e899459d804194a7421278dc317774211d203a7f9c67215bd28f619; 3AB9D23F7A4B3C9B=OGJQCQNVKBREZS63IIDRF5C3FDYRUXTKAA2K36ISTMWXZGH2NZ47WFRSKH23DFAWB4UFYLB52ZQIMA2L6VTT2QMKXQ; areaId=19; ipLoc-djd=19-1601-3637-0; SERVERID=bba5440aed76c583c2b7655e5eb08042; warehistory="4214058,"; wxa_level=1; retina=0; cid=9; webp=1; __jdb=122270672.3.15405259200011633605594|1.1540525920; mba_muid=15405259200011633605594; mba_sid=15405263889006325138283415932.1; __wga=1540526389227.1540526389227.1540526389227.1540526389227.1.1; sc_width=1920; visitkey=48024560612839734; wq_area=19_1601_3637%7C3; shshshfp=62b883f75dabb6f9df16b58b0b9ef0c3; shshshsID=27d3528ef793f237290c4d426bcc04b9_3_1540526389515; autoOpenApp_downCloseDate_auto=1540526389548_21600000; wq_addr=0%7C19_1601_3633_0%7C%u5E7F%u4E1C_%u5E7F%u5DDE%u5E02_%u5929%u6CB3%u533A_%7C%7C; jdAddrId=19_1601_3633_0; jdAddrName=%u5E7F%u4E1C_%u5E7F%u5DDE%u5E02_%u5929%u6CB3%u533A_; commonAddress=0; regionAddress=19%2C1601%2C3633%2C0; mitemAddrId=19_1601_3633_0; mitemAddrName=; wq_logid=1540526408.1611478493; PPRD_P=UUID.15405259200011633605594-LOGID.1540526407859.1345980955""",
    }
    response = requests.get(url="https://item.m.jd.com/product/%s.html" % item_id, headers=headers, data=None)
    if response.status_code == 200:
        open("%s.html" % item_id, "w").write(response.text)
        return response.text
    else:
        print "%s Something Wrong!" % datetime.datetime.now()
        return None


def send_msg(title, content):

    urll = "https://ayiis.me/.send?text=%s&desp=%s" % (title, content)

    response = requests.post(urll, data=None)
    if response.status_code == 200:
        print "send ok!"
    else:
        print "%s Something Wrong!" % datetime.datetime.now()


def loop():

    if get_it(item_id):
        with open("%s.html" % item_id, "r") as f:
            content = f.read()
            ttt = re.findall(r'<script>\s*window\._itemInfo\s*=\s*\((.*?)\)\s*;\s*</script>', content, re.DOTALL | re.M)
            json_ttt = json.loads(ttt[0])
            stock_text = "%s %s %s" % (json_ttt["stock"]["area"]["provinceName"], json_ttt["stock"]["area"]["cityName"], json_ttt["stock"]["StockStateName"])
            stock_text = "%s %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), stock_text)

            if json_ttt["stock"]["StockState"] != 34 or json_ttt["stock"]["StockStateName"] != "\xe6\x97\xa0\xe8\xb4\xa7":
                print "GOOD:", stock_text
                send_msg("\xe8\xb1\xaa\xe8\xbe\xbe\xef\xbc\x88OTARD\xef\xbc\x89 \xe6\xb4\x8b\xe9\x85\x92 XO\xe9\x83\x81\xe9\x87\x91\xe9\xa6\x99\xe5\x9e\x8b\xe9\x85\x92\xe6\x9d\xaf\xe9\x99\x90\xe9\x87\x8f\xe7\x89\x88\xe7\xa4\xbc\xe7\x9b\x92\xe8\xa3\x85 1L", stock_text)
            else:
                print "BAD:", stock_text


def main():
    while True:
        time.sleep(60 + random.randint(1, 20))
        try:
            loop()
        except Exception as e:
            print "Exception:", e


if __name__ == "__main__":
    main()
