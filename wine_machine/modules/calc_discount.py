# coding=utf8
import re
import q
import traceback
from bson.objectid import ObjectId


class JDDiscount(object):
    """
        1
    """
    @classmethod
    def find_discount_by_text(cls, price, text):

        result = re.match(r".*(每满([\d.]+)元，可减([\d.]+)元现金).*", text)
        if result:
            return cls.man_jian_re(price, result.group(1), float(result.group(2)), float(result.group(3)))

        result = re.match(r".*(满([\d.]+)元?减([\d.]+)元?).*", text)
        if result:
            return cls.man_jian(price, result.group(1), float(result.group(2)), float(result.group(3)))

        result = re.match(r".*(满([\d.]+)件，总价打([\d.]+)折).*", text)
        if result:
            return cls.man_zhe(price, result.group(1), float(result.group(2)), float(result.group(3)))

        result = re.match(r".*(满([\d.]+)享([\d.]+)折).*", text)
        if result:
            return cls.man_zhe_num(price, result.group(1), float(result.group(2)), float(result.group(3)))

        result = re.match(r".*(满([\d.]+)元，可减([\d.]+)%).*", text)
        if result:
            return cls.man_minus_percent(price, result.group(1), float(result.group(2)), float(result.group(3)))

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

        return 0, ""     # 没有找到，返回原价

    @classmethod
    def man_jian(cls, price, p_text, num_reach, num_minus):
        """
            1. 满199减20
            2. 满199元减20元

            凑单时，只计算本商品的折扣
        """
        advice = "(%s),不需凑单" % (p_text)
        price_plus = num_reach - price
        # 任何情况都 # 凑单金额小于折扣金额时，补充凑单金额
        if 0 < price_plus < num_reach:  # < num_minus:
            advice = "(%s),需凑单%s元" % (p_text, price_plus)
            # price = price + price_plus
            discount = round(price * (num_minus / num_reach), 2)
        else:
            discount = num_minus

        # discount = round(min(price * (num_minus / num_reach), 2), num_minus)
        # discount = num_minus
        # q.d()
        return discount, advice

    @classmethod
    def man_jian_re(cls, price, p_text, num_reach, num_minus):
        """
            1. 每满300元，可减30元现金
        """
        advice = "(%s),不需凑单" % (p_text)
        price_plus = num_reach - price % num_reach
        # 任何情况都 # 凑单金额小于折扣金额时，补充凑单金额
        if 0 < price_plus < num_reach:  # < num_minus:
            advice = "(%s),需凑单%s元" % (p_text, price_plus)
            # price = price + price_plus

        discount = round(price * (num_minus / num_reach), 2)

        return discount, advice

    @classmethod
    def man_zhe(cls, price, p_text, num_reach, num_minus):
        """
            1. 满2件，总价打8.50折
        """
        advice = "(%s),不需凑单" % (p_text)
        # 凑单金额小于折扣金额时，补充凑单金额
        if num_reach > 1:
            advice = "(%s),需凑单%s件" % (p_text, int(num_reach - 1))
            """
                ⚠️ TODO:

                找到活动链接里价格最优解的凑单品
                目前凑单品价格使用 0 替代
            """

        discount = round(price * (1 - num_minus / 10), 2)

        return discount, advice

    @classmethod
    def man_zhe_num(cls, price, p_text, num_reach, num_minus):
        """
            1. 满399享9折
        """
        advice = "(%s),不需凑单" % (p_text)
        price_plus = num_reach - price
        # 任何情况都 # 凑单金额小于折扣金额时，补充凑单金额
        if 0 < price_plus < num_reach:  # < num_minus:
            advice = "(%s),需凑单%s元" % (p_text, price_plus)

        discount = round(price * (1 - num_minus / 10), 2)
        return discount, advice

    @classmethod
    def man_minus_percent(cls, price, p_text, num_reach, num_minus):
        """
            1. 满138元，可减15%
        """
        advice = "(%s),不需凑单" % (p_text)
        price_plus = num_reach - price
        # 任何情况都 # 凑单金额小于折扣金额时，补充凑单金额
        if 0 < price_plus < num_reach:  # < num_minus:
            advice = "(%s),需凑单%s元" % (p_text, price_plus)

        discount = round(price * (num_minus / 100), 2)
        return discount, advice

    @classmethod
    def calc(cls, item):
        """
        """
        price = float(item["price"])
        if price <= 0:
            item["calc_price"] = price
            item["calc_advice"] = ""
            return item

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
            promote_advice = "活动减%s%s" % (promote_discount, promote_advice)
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
            quan_advice = "券减%s%s" % (quan_discount, quan_advice)
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
        item_list = yield mongodb.DBS["db_wm"]["jingdong_price"].find({
            # "_id": ObjectId("5dafb4bb632c52b5bc74d004"),
        }).to_list(length=None)
        itemid_map = {x["itemid"]: x for x in itemid}
        print("item_list.length:", len(item_list))
        for item in item_list:
            if not itemid_map.get(item["itemid"]):  # or itemid_map.get(item["itemid"])["status"] != 1:
                continue
            try:
                JDDiscount.calc(item)
                yield mongodb.DBS["db_wm"]["jingdong_price"].update_one(
                    {
                        "_id": ObjectId(item["_id"]),
                    }, {
                        "$set": {
                            "calc_price": item["calc_price"],
                            "calc_advice": item["calc_advice"],
                        }
                    },
                )
            except Exception:
                print(traceback.format_exc())
                q.d()

            good_price = itemid_map.get(item["itemid"], {}).get("good_price", 0)
            if item["calc_price"] > 0 and item["calc_price"] < good_price:
                print(item.get("url"))
                print(item.get("name"), "好价：", good_price)
                print(item["price"], "=>", item["calc_price"], "|", item["calc_advice"])
                # print(item)
                print()

        tornado.ioloop.IOLoop.current().stop()

    main()
    tornado.ioloop.IOLoop.current().start()


def test2():
    item = {}
    JDDiscount.calc(item)
    print(item["price"])
    print(item["quan"])
    print(item["promote"])
    print(item["calc_price"], item["calc_advice"])


if __name__ == "__main__":
    # JDDiscount.calc(item)
    # # print(item)
    # print(item["price"])
    # print(item["quan"])
    # print(item["promote"])
    # print(item["calc_price"], item["calc_advice"])

    # test2()
    test()
