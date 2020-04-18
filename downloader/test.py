import core
import os
import re
import q
"""
    https://www.baidu.com/img/bd_logo.png
    TODO:
        1. 下载的最终网址是跳转后的网址，则获取到的host是错误的
            - done
        2. Working on 'Accept-Ranges': 'bytes' => 抓包迅雷吧
            - 没想到竟然是 bytes 的大小写问题
            - done
        3. nginx存在 transfer-encoding 覆盖 range 的问题
            一般情况下 transfer-encoding 和 content-encodeing 不会共存
            - 在请求header和多线程下载时移除 Accept-Encoding
            - done
        4. 批量下载多个文件
            - Is it necessary?

        5. 下载 Google drive
            ✅ https://drive.google.com/uc?id=1KcMYcNJgtK1zZvfl_9sTqnyBUTri2aP2&export=download
            实测cooker02使用了4线程会超时，目前使用2线程
            需要完整 header
            下载链接过期时间太快，3分钟没有tcp包交换就直接失败了
                - 看来需要补链功能 + 断点续传
            使用 cooker02 不稳定，一旦挂了那就下载失败了
            ❌ [ERROR] Something is wrong.
"""


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
        "target_url": "https://about.cnblogs.com/",
        "file_name": "about.html",
        "md5": "e5b503e23d3c2b180722d4c18f54d3fc",
    }
    do_test(args)

    args = {
        "target_url": "https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo/bd_logo1_31bdc765.png",
        "file_name": "bd_logo1_31bdc765.png",
        "md5": "2885cdb57f913ed832df4a0731bdc765",
    }
    do_test(args)

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
        "target_url": "https://ayiis.me/aydocs/readme.txt",
        "file_name": "readme.txt",
        "md5": "9495df25b9b9d1a04d14b17923961760",
    }
    do_test(args)

    args = {
        "target_url": "http://image3.uuu9.com/war3/war3rpg/UploadFiles_1951/201910/201910181520141521.jpg",
        "file_name": "201910181520141521.jpg",
        "md5": "290d04aa104106f1ac1515fe67b0340c",
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
        "target_url": "https://ayiis.me/aydocs/download/xx10240_8",
        "file_name": "xx10240_8",
        "md5": "030a4f48dc8db0956add25994004e5ca",
    }
    do_test(args)

    args = {
        "target_url": "https://ayiis.me/aydocs/edu.max.js",
        "file_name": "edu.max.js",
        "md5": "234ffe028394dcad430ec296f4496fc5",
    }
    do_test(args)

    args = {
        "target_url": "https://warehouse-camo.cmh1.psfhosted.org/807e4b51537640bee0aa77064dc577ee1669a4fd/68747470733a2f2f6661726d352e737461746963666c69636b722e636f6d2f343331372f33353139383338363337345f313933396166336465365f6b5f642e6a7067",
        "file_name": "807e4b51537640bee0aa77064dc577ee1669a4fd.jpg",
        "md5": "eb489d987e41bb561131f6d3f2fa81ab",
    }
    do_test(args)


def multi_proc():

    # for i in range(1, 63):
    #     rno = str(i).rjust(3, "0")
    #     print("https://pic.kissgoddess.com/gallery/26679/28022/%s.jpg" % rno)
        # args = {
        #     "target_url": "https://pic.kissgoddess.com/gallery/26679/28022/%s.jpg" % rno,
        #     "file_name": "%s.jpg" % rno,
        #     "max_thread": 3,
        # }
        # db = core.DownloadBuilder(args)
        # db.start_task()
        # q.d()

    zzz = [
        "http://ayiis.me/aydocs/download/hand/MOHI-S1-P1-50.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S1-P51-100.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S1-P101-150.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S1-P151-200.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S2-P1-50.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S2-P51-100.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S2-P101-150.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S2-P151-200.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S3-P1-50.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S3-P51-100.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S3-P101-150.rar",
        "http://ayiis.me/aydocs/download/hand/MOHI-S3-P151-200.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S1-P1-50.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S1-P51-100.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S1-P101-150.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S1-P151-200.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S2-P1-50.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S2-P51-100.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S2-P101-150.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S2-P151-200.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S3-P1-50.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S3-P51-100.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S3-P101-150.rar",
        "http://ayiis.me/aydocs/download/hand/WEHI-S3-P151-200.rar"
    ]
    for z in zzz:
        args = {
            "target_url": z,
            "file_name": z.split("/")[-1],
            "max_thread": 3,
        }
        db = core.DownloadBuilder(args)
        db.start_task()


if __name__ == "__main__":
    multi_proc()
    # test()
