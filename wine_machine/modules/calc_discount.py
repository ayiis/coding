# coding=utf8
import re
import q


class JDDiscount(object):
    """
        1
    """
    @classmethod
    def find_discount_by_text(cls, price, text):

        result = re.match(r".*每满([\d.]+)元，可减([\d.]+)元现金.*", text)
        if result:
            return cls.man_jian_re(price, float(result.group(1)), float(result.group(2)))

        result = re.match(r".*满([\d.]+)元?减([\d.]+)元?.*", text)
        if result:
            return cls.man_jian(price, float(result.group(1)), float(result.group(2)))

        result = re.match(r".*满([\d.]+)件，总价打([\d.]+)折.*", text)
        if result:
            return cls.man_zhe(price, float(result.group(1)), float(result.group(2)))

        result = re.match(r".*满([\d.]+)享([\d.]+)折.*", text) or re.match(r".*满([\d.]+)元，可减([\d.]+)%.*", text)
        if result:
            return cls.man_zhe_num(price, float(result.group(1)), float(result.group(2)))
        if "换购" in text:
            pass
        elif "即赠" in text:
            pass
        elif "赠品" in text:
            pass
        elif "满" == text:
            pass
        else:
            print("[404 not found]", text)
            raise 1

        return 0, ""     # 没有找到，返回原价

    @classmethod
    def man_jian(cls, price, num_reach, num_minus):
        """
            1. 满199减20
            2. 满199元减20元

            凑单时，只计算本商品的折扣
        """
        advice = "不需凑单"
        price_plus = num_reach - price
        # 任何情况都 # 凑单金额小于折扣金额时，补充凑单金额
        if 0 < price_plus < num_reach:  # < num_minus:
            advice = "需凑单%s元" % (price_plus)
            # price = price + price_plus
            discount = round(price * (num_minus / num_reach), 2)
        else:
            discount = num_minus

        # discount = round(min(price * (num_minus / num_reach), 2), num_minus)
        # discount = num_minus
        # q.d()
        return discount, advice

    @classmethod
    def man_jian_re(cls, price, num_reach, num_minus):
        """
            1. 每满300元，可减30元现金
        """
        advice = "不需凑单"
        price_plus = num_reach - price % num_reach
        # 任何情况都 # 凑单金额小于折扣金额时，补充凑单金额
        if 0 < price_plus < num_reach:  # < num_minus:
            advice = "需凑单%s元" % (price_plus)
            # price = price + price_plus

        discount = round(price * (num_minus / num_reach), 2)

        return discount, advice

    @classmethod
    def man_zhe(cls, price, num_reach, num_minus):
        """
            1. 满2件，总价打8.50折
        """
        advice = "不需凑单"
        # 凑单金额小于折扣金额时，补充凑单金额
        if num_reach > 1:
            advice = "需凑单%s件" % (int(num_reach - 1))
            """
                ⚠️ TODO:

                找到活动链接里价格最优解的凑单品
                目前凑单品价格使用 0 替代
            """

        discount = round(price * (1 - num_minus / 10), 2)

        return discount, advice

    @classmethod
    def man_zhe_num(cls, price, num_reach, num_minus):
        """
            1. 满399享9折
            2. 满138元，可减15%
        """
        advice = "不需凑单"
        price_plus = num_reach - price
        # 任何情况都 # 凑单金额小于折扣金额时，补充凑单金额
        if 0 < price_plus < num_reach:  # < num_minus:
            advice = "需凑单%s元" % (price_plus)

        discount = round(price * (1 - num_minus / 10), 2)
        return discount, advice

    @classmethod
    def calc(cls, item):
        """
        """
        price = int(float(item["price"]))

        # 计算活动
        promote_price_map = {}
        for promote in set([x[0] for x in item["promote"]]):
            texts = promote.split("；")
            for text in texts:
                discount, advice = cls.find_discount_by_text(price, text)
                promote_price_map[discount] = advice

        promote_discount = promote_price_map and max(promote_price_map) or 0
        promote_advice = promote_price_map.get(promote_discount)
        if promote_advice:
            promote_advice = "活动减%s,%s" % (promote_discount, promote_advice)
        else:
            promote_advice = "无活动"

        # 计算优惠券
        quan_price_map = {}
        for quan in set([x[0] for x in item["quan"]]):
            text = quan
            discount, advice = cls.find_discount_by_text(price, text)
            quan_price_map[discount] = advice

        quan_discount = quan_price_map and max(quan_price_map) or 0
        quan_advice = quan_price_map.get(quan_discount)
        if quan_advice:
            quan_advice = "券减%s,%s" % (quan_discount, quan_advice)
        else:
            quan_advice = "无券"

        item["calc_price"] = round(price - promote_discount - quan_discount, 2)
        item["calc_advice"] = "%s; %s" % (promote_advice, quan_advice)

        return item


def test():
    import tornado.ioloop
    import tornado.gen
    import sys
    sys.path.insert(0, "/mine/github/coding/wine_machine/common/")
    import mongodb

    @tornado.gen.coroutine
    def main():
        yield mongodb.init({"db_wm": {
            "HOST": "127.0.0.1",
            "PORT": 27017,
            "DATABASE_NAME": "wm",
            "USERNAME": "",
            "PASSWORD": "",
        }})
        itemid = yield mongodb.DBS["db_wm"]["jingdong_itemid"].find({}).to_list(length=None)
        item_list = yield mongodb.DBS["db_wm"]["jingdong_price_old"].find({}).to_list(length=None)
        itemid_map = {x["itemid"]: x for x in itemid}
        print("item_list.length:", len(item_list))

        for item in item_list:
            if not itemid_map.get(item["itemid"]) or itemid_map.get(item["itemid"])["status"] != 1:
                continue
            if float(item["price"]) <= 0:
                continue
            try:
                JDDiscount.calc(item)
            except Exception:
                q.d()

            good_price = itemid_map.get(item["itemid"], {}).get("good_price", 0)
            if item["calc_price"] < good_price:
                print(item["url"])
                print(item.get("name"), "好价：", good_price)
                print(item["price"], "=>", item["calc_price"], "|", item["calc_advice"])
                print(item)
                print()

        tornado.ioloop.IOLoop.current().stop()

    main()
    tornado.ioloop.IOLoop.current().start()


def test2():
    # item = {'itemid': '4279786', 'cat': '12259,14715,14738', 'name': '【人头马X.O】人头马（Remy Martin）洋酒 XO优质香槟区干邑白兰地700ml 2019中秋礼盒', 'shopId': '1000016184', 'venderId': '1000016184', 'price': '1669.00', 'vender': '人头马君度京东自营专区', 'stock': '无货', 'promote': [], 'gift': [['会员特价', '2019-11-09 23:59:59']], 'quan': [['满168享8.5折', '2019-11-01 ~ 2019-11-11'], ['满399享9折', '2019-11-04 ~ 2019-11-07'], ['满199减120', '2019-11-01 ~ 2019-11-14']], 'feedback': '', 'ads': ['【爆款低至8折】11.11震撼开启，人头马品牌秒杀火热进行时，爆款直降好礼相赠，让你11.11好价提前享！&lt;a href="https://pro.jd.com/mall/active/3bnrWZtyu3LSpDAz5bRm9rbL5DX8/index.html" target="_blank"&gt;点击抢购！&lt;/a&gt;'], 'datetime': '2019-11-04 08:04:14', 'url': 'https://item.jd.com/4279786.html', 'presale': False, 'good_price': 1000, 'calc_price': 662.57, 'calc_advice': '无活动; 券减1006.43,不需凑单'}
    item = {'itemid': '100005316802', 'url': 'https://item.jd.com/100005316802.html', 'name': '【猴王猴王】猴王 (Monkey 47 gin) 猴王47 黑森林 楒洛金酒风味 配制酒 500ml', 'cat': '12259,14715,14746', 'venderId': '1000097462', 'shopId': '1000097462', 'price': '409.00', 'vender': '保乐力加洋酒京东自营专区', 'stock': '现货', 'promote': [['满299元减60元', 'https://search.jd.com/Search?activity_id=50038001671', '2019-09-25 00:00:00 ~ 2019-09-27 23:59:59']], 'gift': [], 'quan': [['满499减100', '2019-09-25 ~ 2019-09-30'], ['满499减100', '2019-09-25 ~ 2019-09-30']], 'feedback': '', 'ads': ["此商品将于2019-09-28,00点结束闪购特卖，&lt;a target='_blank' href='http://red.jd.com/redList-395888-28.html?pr=16'&gt;洋酒迎国庆&lt;/a&gt;"], 'datetime': '2019-09-26 01:58:16', 'calc_price': 249.0, 'calc_advice': '活动减60.0,不需凑单; 券减100.0,需凑单90.0元'}
    JDDiscount.calc(item)
    print(item["price"])
    print(item["quan"])
    print(item["promote"])
    print(item["calc_price"], item["calc_advice"])


if __name__ == "__main__":
    # item = {'itemid': '43871571802', 'cat': '12259,14714,15601', 'name': '【匈牙利国家馆】原瓶进口葡萄酒 国营酒庄大托卡伊5篓贵腐Aszu阿苏甜白女士葡萄酒 送礼 单支赠礼袋', 'shopId': '898568', 'venderId': '10055004', 'price': '248.00', 'vender': '匈牙利国家馆', 'stock': '现货', 'promote': [['每满248元，可减20元现金', 'https://search.jd.com/Search?activity_id=31047052572', '2019-11-01 00:00:00 ~ 2019-11-15 23:59:00']], 'gift': [], 'quan': [['满399减100', '2019-11-04 ~ 2019-11-04']], 'feedback': '', 'ads': ['【匈牙利国家馆】甄选酒品，品质保证，一起探寻匈牙利奇妙之旅\n【京东好物节】好物提前购，好货提前到，11月1日-11月11日，全馆价保。&lt;a href="https://mall.jd.com/index-898568.html" target="_blank"&gt;更多活动，请戳&lt;/a&gt;'], 'datetime': '2019-11-04 17:01:28', 'url': 'https://item.jd.com/43871571802.html', 'good_price': 148, 'presale': False, 'calc_price': 128.0, 'calc_advice': '活动减20.0,不需凑单; 券减100.0,不需凑单'}
    # JDDiscount.calc(item)
    # # print(item)
    # print(item["price"])
    # print(item["quan"])
    # print(item["promote"])
    # print(item["calc_price"], item["calc_advice"])

    # test2()
    test()
