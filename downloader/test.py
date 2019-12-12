import core
import os
import re
import q


def execute_command(cmd):
    ret = os.popen(cmd)
    return ret.read()


def do_test(args):

    db = core.DownloadBuilder(args)
    db.start_task()

    md5_re = execute_command("md5sum %s" % args["file_name"])

    if "%s  %s\n" % (args["md5"], args["file_name"]) == md5_re:
        print("[✅ PASS] %s" % args["file_name"])
    else:
        print("[❌ FAIL] %s" % args["file_name"])
    print()


def test():
    args = {
        # "target_url": "https://news.cnblogs.com/",
        # "target_url": "https://ayiis.me/",
        # "target_url": "https://ayiis.me/aydocs/UltraEdit32.rar",    # e9f89cbc70b02bb17d081fb60d7a9663
        # "target_url": "https://ayiis.me/aydocs/download/ex.zip",   # 61749db2be5027cebde151c307777c6d
        # "target_url": "https://ayiis.me/aydocs/download/fff.zip",    # 965e2c518542d7be0748757ac168e425
        # "target_url": "https://ayiis.me/aydocs/download/xx1024.file",    # 0f343b0931126a20f133d67c2b018a3b
        # "target_url": "https://ayiis.me/aydocs/download/xx10240.file",    # 1276481102f218c981e0324180bafd9f
        # "target_url": "https://ayiis.me/aydocs/download/xx102400.file",    # 4c6426ac7ef186464ecbb0d81cbfcb1e
        # "target_url": "https://ayiis.me/aydocs/download/xx10240_16",    # 6cc3d8ecd5a9967c9227be8d17b988a6
        # "target_url": "https://ayiis.me/aydocs/download/xx10240_8",    # 030a4f48dc8db0956add25994004e5ca
        # "target_url": "https://ayiis.me/aydocs/download/xx10240_8+1",    # 380395a711ac160a1887d8a046eb4ba1
        # "target_url": "https://ayiis.me/aydocs/download/xx10240_8-1",    # 929d7d6bd36b6f8879370ca24674cc81
        "target_url": "https://ayiis.me/aydocs/readme.txt",        # 9495df25b9b9d1a04d14b17923961760
        # "target_url": "https://img2018.cnblogs.com/news/34358/201912/34358-20191211155626893-1187684302.jpg",        #
        # "target_url": "https://1-im.guokr.com/LAQ0touxN2eFtub6GZ0Nm6EEq3UV8muBo5ojuymziDtQEAAAgAYAAEpQ.jpg?imageView2/1/w/648/h/356",        #
        # "target_url": "https://pic1.zhimg.com/50/v2-188092cbfc0d010a96a22374eaea9877_hd.jpg",        #
        # "target_url": "https://img.iplaysoft.com/wp-content/uploads/2019/aliyun-sale/aliyun_201912_2x.jpg",        #
        # "target_url": "http://image3.uuu9.com/war3/war3rpg/UploadFiles_1951/201910/201910181520141521.jpg",        #
        # "target_url": "http://war3down1.uuu9.com/war3/201404/201404081001.rar",        #
        # "target_url": "http://war3down1.uuu9.com/war3/201911/201911251725.rar",
        # "target_url": "https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo/bd_logo1_31bdc765.png",
        # "target_url": "https://warehouse-camo.cmh1.psfhosted.org/807e4b51537640bee0aa77064dc577ee1669a4fd/68747470733a2f2f6661726d352e737461746963666c69636b722e636f6d2f343331372f33353139383338363337345f313933396166336465365f6b5f642e6a7067",
        # "file_name": "baidu.png",
        "file_name": "ex.zip",
        # "file_name": "201911251725.rar",
    }

    args = {
        "target_url": "https://1-im.guokr.com/LAQ0touxN2eFtub6GZ0Nm6EEq3UV8muBo5ojuymziDtQEAAAgAYAAEpQ.jpg?imageView2/1/w/648/h/356",
        "file_name": "DtQEAAAgAYAAEpQ.jpg",
        "md5": "9b11c7b9cd8f4ba3186b9d0e6e6e98db",
    }
    do_test(args)

    args = {
        "target_url": "https://pic1.zhimg.com/50/v2-188092cbfc0d010a96a22374eaea9877_hd.jpg",
        "file_name": "eaea9877_hd.jpg",
        "md5": "384ca6a29ab14c16b6f20812f67bf484",
    }
    do_test(args)

    args = {
        "target_url": "https://img.iplaysoft.com/wp-content/uploads/2019/aliyun-sale/aliyun_201912_2x.jpg",
        "file_name": "aliyun_201912_2x.jpg",
        "md5": "f3d679a2af24b805288475b5bc1d119b",
    }
    do_test(args)

    # return

    args = {
        "target_url": "https://img2018.cnblogs.com/news/34358/201912/34358-20191211155626893-1187684302.jpg",
        "file_name": "1187684302.jpg",
        "md5": "0c420808766eaa3b349a3f6e6adc6bd2",
    }
    do_test(args)

    args = {
        "target_url": "https://ayiis.me/aydocs/download/xx10240_8",
        "file_name": "xx10240_8",
        "md5": "030a4f48dc8db0956add25994004e5ca",
    }
    do_test(args)

    args = {
        "target_url": "https://ayiis.me/aydocs/readme.txt",
        "file_name": "readme.txt",
        "md5": "9495df25b9b9d1a04d14b17923961760",
    }
    do_test(args)

    args = {
        "target_url": "http://war3down1.uuu9.com/war3/201911/201911251725.rar",
        "file_name": "201911251725.rar",
        "md5": "dc2d581f228c2a2721408b6b61d1959b",
    }
    do_test(args)

    args = {
        "target_url": "https://ayiis.me/aydocs/readme.txt",
        "file_name": "readme.txt",
        "md5": "9495df25b9b9d1a04d14b17923961760",
    }
    do_test(args)

    args = {
        "target_url": "https://ayiis.me/aydocs/download/xx10240_8-1",
        "file_name": "xx10240_8-1",
        "md5": "929d7d6bd36b6f8879370ca24674cc81",
    }
    do_test(args)

    args = {
        "target_url": "https://ayiis.me/aydocs/download/xx10240_8+1",
        "file_name": "xx10240_8+1",
        "md5": "380395a711ac160a1887d8a046eb4ba1",
    }
    do_test(args)


if __name__ == "__main__":
    test()
