"""
    为了应对日益严重的 tcp 中断情况


    TODO:
        ok 1. try and find how Chrome resume download
            - shutdown wifi to make it broke

        2. how to speed up single thread downloader
            - seems no way

        ok 3. Try skip dns
            - cache the ip and port
"""
import q
import re
import time
import traceback
import threading
import queue
import socket
import urllib3
import requests
from requests_toolbelt.adapters import host_header_ssl

# stupid thing
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KB = 1024
CHUNK_SIZE = (256 * KB)                     # 每个线程一次下载的大小 ?256KB
CHUNK_TIMEOUT = CHUNK_SIZE // (16 * KB)      # 每个线程一次下载速度最慢 ?4KB/s 超时
HEAD_TIMEOUT = CHUNK_SIZE // CHUNK_TIMEOUT // KB * 2 + 5  # 2: header视作2KB; 5: 适应值
THREAD_MAX = 6                             # 最大线程数量 ?6 个
READ_CHUNK_SIZE = requests.models.CONTENT_CHUNK_SIZE or (10 * 1024)


def pretty_file_size(byte):
    """
        格式化文件尺寸 最小是B，最大是T
    """
    size = ["B", "K", "M", "G", "T"]
    i = 0
    res = byte
    while 1000 < res:
        res = res / KB
        i = i + 1
        if i == len(size) - 1:
            break

    return "%s%s" % (round(res, 2), size[i])


god_mode_setting = {
    "cache_create_connection": None,
    "cache_addr_list": [],
    "cache_addr_counter": 0,
}


def god_mode():

    if god_mode_setting["cache_create_connection"] is None:
        god_mode_setting["cache_addr_list"] = list(set(god_mode_setting["cache_addr_list"]))
        god_mode_setting["cache_create_connection"] = urllib3.util.connection.create_connection
        print("Host list:", god_mode_setting["cache_addr_list"])

    def next_god_mode():
        if god_mode_setting["cache_addr_counter"] == len(god_mode_setting["cache_addr_list"]) - 1:
            god_mode_setting["cache_addr_counter"] = 0
        else:
            god_mode_setting["cache_addr_counter"] += 1

    def wrap_create_connection(address, *argc, **argv):

        new_address = (god_mode_setting["cache_addr_list"][god_mode_setting["cache_addr_counter"]], address[1])
        # print("new_address: %s -> %s" % (address, new_address))
        next_god_mode()
        return god_mode_setting["cache_create_connection"](new_address, *argc, **argv)

    urllib3.util.connection.create_connection = wrap_create_connection


class Wrapper(object):
    def __init__(self, arg):
        super(Wrapper, self).__init__()
        self.target_url = arg["target_url"]
        self.file_name = arg["file_name"]
        self.task_queue = queue.Queue()
        self.task_finish_count = 0
        self.task_total_count = 0
        self.target_host = re.match(r"http[s]?://([^/]+)", self.target_url).group(1)
        self.target_addr = None
        self.last_task = None
        self.last_task_done = False
        self.lock = threading.Lock()
        self.lock2 = threading.Lock()
        self.lock_file = threading.Lock()
        self.fail_times = 0
        self.download_finished = False
        self.header_info_done = False
        self.dns_query_done = False
        print(
            "KB:", KB,
            ", CHUNK_SIZE:", pretty_file_size(CHUNK_SIZE),
            ", CHUNK_TIMEOUT:", CHUNK_TIMEOUT,
            ", HEAD_TIMEOUT:", HEAD_TIMEOUT,
            ", THREAD_MAX:", THREAD_MAX,
        )

    def split_task(self):
        """
            将任务切割成多份，采用生成器形式
            如果任务小于 CHUNK_SIZE 就不切割了
        """
        self.file_size / CHUNK_SIZE
        tmp_size = 0

        while tmp_size < self.file_size:
            self.task_queue.put({
                "start": tmp_size,
                "end": min(tmp_size + CHUNK_SIZE, self.file_size),
            })
            tmp_size = tmp_size + CHUNK_SIZE

        self.task_total_count = self.task_queue.qsize()

    def get_next_task(self):
        """
            use lock to make sure
        """
        try:
            self.lock.acquire()

            task = None
            if self.task_queue.empty():
                if self.last_task:
                    task, self.last_task = self.last_task, None
            else:
                task = self.task_queue.get()
                if self.task_queue.empty():
                    task["is_last"] = True
                    self.last_task = task

            return task

        except Exception:
            pass
        finally:
            self.lock.release()

    def fail_task(self, task):
        # self.task_queue.put(task)
        self.fail_times += 1
        print("[WARNING] Total fail: %s / %s" % (self.fail_times, self.task_total_count))

    def finish_task(self, task):

        try:
            self.lock2.acquire()

            if self.task_finish_count == self.task_total_count:
                return

            self.task_finish_count += 1
            self.touch_status_bar()

            if self.task_finish_count == self.task_total_count:
                self.finish_status_bar()

        finally:
            self.lock2.release()

    def header_print(self, *argv):
        if self.header_info_done:
            return
        else:
            print(*argv)

    def get_header_info(self, queue_out):
        """
            获取内容总长度 并验证是否支持 Range 方式下载
        """
        headers = {
            "Range": "Bytes=0-43",  # a wav header length is 44
            "Accept-Encoding": "*",
        }
        # 重试3次
        for i in range(3):
            if self.header_info_done:
                break
            try:
                res = requests.get(
                    self.target_url,
                    headers=headers,
                    timeout=HEAD_TIMEOUT,
                    stream=True,
                    # verify=False,
                )
                hcr = res.headers.get("Content-Range")

                peer = res.raw._fp.fp.raw._sock.getpeername()
                self.target_addr = "%s:%s" % (peer[0], peer[1])

                god_mode_setting["cache_addr_list"].append(peer[0])

                if not hcr:
                    self.header_print("Not suit for content-range.")
                    self.header_print(res.headers)
                    queue_out.put(0)
                    break

                content = res.raw.read(49)     # only for content

                self.file_size = int(hcr.split("/")[1])
                if not (len(content) == 44 and hcr == "bytes 0-43/%s" % (self.file_size)):
                    self.header_print("Len not good: %s" % len(content))
                    queue_out.put(0)
                    break

            except requests.exceptions.ReadTimeout:
                self.header_print("Get header info: ReadTimeout..")
            except Exception:
                self.header_print(traceback.format_exc())
            else:
                queue_out.put(self.file_size)
                break

        # 3次都失败了，告诉外面不用等待了
        queue_out.put(0)

    def double_finger(self):
        """
            并发获取内容总长度, 通过 queue_out 通知主线程
        """
        queue_out = queue.Queue()

        for i in range(2):
            thread = threading.Thread(target=self.give_me_five)
            thread.start()

        for i in range(2):
            thread = threading.Thread(target=self.get_header_info, args=(queue_out, ))
            thread.start()

        return queue_out.get()

    def give_me_five(self):

        for i in range(3):
            if self.dns_query_done:
                break
            try:
                dns_result = socket.getaddrinfo(self.target_host, 0, 0, 0, 0)
                god_mode_setting["cache_addr_list"] = list(set([z[-1][0] for z in dns_result]))
                self.dns_query_done = True
                break
            except Exception:
                if not self.dns_query_done:
                    self.header_print(traceback.format_exc())

    def write_file(self, content, seek=None):

        try:
            self.lock_file.acquire()

            if seek is not None:
                self.fd.seek(seek)

            self.fd.write(content)

        finally:
            self.lock_file.release()

    def do_task(self):
        """
            1
        """
        with requests.Session() as session:
            # Speed up: skip the dns query by SSLAdapter
            # Must use `verify=False` to avoid:
            # SSLCertVerificationError("hostname 'a.com' doesn't match either of 'b.com', 'c.com'")
            # session.mount("https://", host_header_ssl.HostHeaderSSLAdapter())
            # target_url = re.sub(
            #     r"^(http[s]?\://)%s([/]?)" % self.target_host,
            #     r"\g<1>%s\g<2>" % self.target_addr,
            #     self.target_url,
            #     flags=re.I
            # )
            target_url = self.target_url
            retry = False
            content = b""

            while True:

                if not retry:
                    task = self.get_next_task()
                    if task is None:
                        # print("task done", "exit thread.")
                        return None

                if "is_last" in task:
                    is_last = True
                else:
                    is_last = False

                try:

                    headers = {
                        # "Host": self.target_host,
                        # `start` <= Range <= `end`, So `end` should -1
                        "Range": "Bytes=%s-%s" % (task["start"] + len(content), task["end"] - 1),
                        "Accept-Encoding": "*",
                    }
                    res = session.get(
                        target_url,
                        headers=headers,
                        timeout=(5, CHUNK_TIMEOUT),
                        stream=True,
                        # verify=False,
                    )

                    while True:
                        if is_last and self.last_task_done:
                            # raise Exception("Last is done.")
                            return None
                        if len(content) == task["end"] - task["start"]:
                            break

                        content += res.raw.read(READ_CHUNK_SIZE)     # no headers, only the content

                    # DEBUG: never should this happened.
                    if len(content) != task["end"] - task["start"]:
                        print("[ERROR] Not suit: %s != %s ; from %s to %s" % (
                            len(content),
                            task["end"] - task["start"],
                            task["start"],
                            task["end"],
                        ))
                        print(res.headers)
                        raise Exception("Not suitable.")

                    self.write_file(content, task["start"])

                except (urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
                    if is_last and self.last_task_done:
                        retry = False
                    else:
                        retry = True
                    self.fail_task(task)

                except Exception:
                    print(traceback.format_exc())
                    if is_last and self.last_task_done:
                        retry = False
                    else:
                        retry = True
                    self.fail_task(task)

                else:
                    content = b""
                    retry = False
                    if is_last:
                        if not self.last_task_done:
                            self.last_task_done = True
                            self.finish_task(task)
                    else:
                        self.finish_task(task)
                finally:
                    time.sleep(0.2)

    def single_line_downloader(self):

        thread = threading.Thread(target=self.start_single_line_bar, args=())
        thread.start()

        self.fd = open(self.file_name, "wb+")
        with requests.Session() as session:
            res = session.get(
                self.target_url,
                headers={
                    "Accept-Encoding": "*"
                },
                timeout=180,
                stream=True,
            )

            while True:
                content = res.raw.read(READ_CHUNK_SIZE)     # no headers, only the content
                if not content:
                    break
                self.write_file(content)
                self.touch_download_speed(READ_CHUNK_SIZE)  # no need to use len(content)

        self.download_finished = True
        self.finish_single_line_bar()
        self.fd.close()

    def touch_download_speed(self, chunk_size):
        """
            存储并返回前5秒的平均下载速度
            在 get_download_speed 计算
        """
        if not hasattr(self, "init_ts"):
            self.init_ts = time.time()
            self.ts_counter = {
                "total_size": 0
            }

        ts_counter = self.ts_counter

        self.now_ts_s = int(time.time() - self.init_ts)
        ts_counter[self.now_ts_s] = ts_counter.get(self.now_ts_s, 0) + chunk_size
        ts_counter["total_size"] += chunk_size

        if ts_counter.get(self.now_ts_s - 6):
            del ts_counter[self.now_ts_s - 6]

    def get_download_speed(self):
        """
            计算下载速度
        """
        total_size = 0
        total_ts = 0
        for i in range(self.now_ts_s, self.now_ts_s - 6, -1):
            if i in self.ts_counter:
                total_size += self.ts_counter[i]
                total_ts += 1

        return pretty_file_size(total_size / max(total_ts, 1))

    def finish_single_line_bar(self):
        # self._status_bar.finish()
        pass

    def touch_single_line_bar(self):
        if self.download_finished:
            self._status_bar.phases = [" "]
            ts_s = round(time.time() - self.init_ts, 2)
            self._status_bar.message = "Total Size: %s, Total Time: %ss, Avg Speed: %s/s " % (
                pretty_file_size(self.ts_counter["total_size"]),
                ts_s,
                pretty_file_size(self.ts_counter["total_size"] / max(ts_s, 1)),
            )
            self._status_bar.message = self._status_bar.message.ljust(49, " ")
            self._status_bar.next()
            self._status_bar.finish()
            print("Done.")
        else:
            self._status_bar.message = "Got: %s, Speed: %s/s " % (
                pretty_file_size(self.ts_counter["total_size"]),
                self.get_download_speed()
            )
            self._status_bar.message = self._status_bar.message.ljust(36, " ")
            self._status_bar.next()

    def start_single_line_bar(self):
        from progress.spinner import Spinner
        Spinner.phases = ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛']
        self.touch_download_speed(0)
        self._status_bar = Spinner("Init downloader.. ")
        self._status_bar.next()

        while not self.download_finished:
            self.touch_download_speed(0)
            self.touch_single_line_bar()
            time.sleep(0.2)

        self.touch_single_line_bar()

    def start_task(self):

        # 获取文件尺寸，测试是否支持 range 方式（多线程，断点续传）
        ts = time.time()
        res = self.double_finger()
        self.header_info_done = True
        if res <= 0:
            print("[WANRING] start single line downloader..")
            return self.single_line_downloader()

        # 查 DNS，如果堵塞了，等待3秒（本心：为了应对垃圾网络）
        for i in range(30):
            if not self.dns_query_done:
                time.sleep(0.1)

        # 强制使用指定IP解析域名，提高速度
        peer_ip, peer_port = self.target_addr.split(":")
        god_mode()

        self.split_task()
        print("Get server info: %s -> %s" % (self.target_host, self.target_addr))
        print("Get file info: %ss, download chunk: %s" % (round(time.time() - ts, 3), self.task_queue.qsize()))

        # 预先分配空间
        self.fd = open(self.file_name, "wb+")
        self.fd.seek(self.file_size)
        self.write_file(b"")

        ts = time.time()
        print(
            "[⏱ START]",
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            "File size:", pretty_file_size(self.file_size),
        )
        print()

        self.create_status_bar()

        thread_list = []
        for i in range(THREAD_MAX):

            thread = threading.Thread(target=self.do_task, args=())
            thread.start()
            thread_list.append(thread)

        for i in thread_list:
            i.join()

        self.fd.close()

        print()
        print(
            "[✅ DONE]",
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            "Total time: %ss" % round(time.time() - ts, 3),
            "Avg speed: %s/s" % pretty_file_size(self.file_size / max(time.time() - ts, 1)),
        )

    def create_status_bar(self):
        from progress.bar import Bar
        self._status_bar = Bar("Download status:", fill="█", max=self.task_total_count, suffix="%(percent)d%%")

    def touch_status_bar(self):
        self._status_bar.next()

    def finish_status_bar(self):
        self._status_bar.finish()


def main():

    args = {
        # "target_url": "https://ayiis.me/",
        # "target_url": "https://ayiis.me/aydocs/UltraEdit32.rar,    # e9f89cbc70b02bb17d081fb60d7a9663
        # "target_url": "https://ayiis.me/aydocs/download/ex.zip",    # 61749db2be5027cebde151c307777c6d
        # "target_url": "https://ayiis.me/aydocs/readme.txt",        # 9495df25b9b9d1a04d14b17923961760
        # "target_url": "https://img2018.cnblogs.com/news/34358/201912/34358-20191211155626893-1187684302.jpg",        #
        # "target_url": "https://1-im.guokr.com/LAQ0touxN2eFtub6GZ0Nm6EEq3UV8muBo5ojuymziDtQEAAAgAYAAEpQ.jpg?imageView2/1/w/648/h/356",        #
        # "target_url": "https://pic1.zhimg.com/50/v2-188092cbfc0d010a96a22374eaea9877_hd.jpg",        #
        # "target_url": "https://img.iplaysoft.com/wp-content/uploads/2019/aliyun-sale/aliyun_201912_2x.jpg",        #
        # "target_url": "http://image3.uuu9.com/war3/war3rpg/UploadFiles_1951/201910/201910181520141521.jpg",        #
        "target_url": "http://war3down1.uuu9.com/war3/201404/201404081001.rar",        #
        # "target_url": "http://war3down1.uuu9.com/war3/201911/201911251725.rar",
        # "target_url": "https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo/bd_logo1_31bdc765.png",
        # "file_name": "baidu.png",
        # "file_name": "https://warehouse-camo.cmh1.psfhosted.org/807e4b51537640bee0aa77064dc577ee1669a4fd/68747470733a2f2f6661726d352e737461746963666c69636b722e636f6d2f343331372f33353139383338363337345f313933396166336465365f6b5f642e6a7067",
        "file_name": "ex.zip",
        # "file_name": "201911251725.rar",
    }
    w = Wrapper(args)

    w.start_task()


def test_session():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    r = s.get("https://ayiis.me/aydocs/UltraEdit32.rar", timeout=(3, 1))
    print(r.text[:20])


def test_stream():
    res = requests.get("https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo/bd_logo1_31bdc765.png", timeout=(3, 3), stream=True)
    head = res.raw.read(44)     # only about content
    print("head:", head)
    peer = res.raw._fp.fp.raw._sock.getpeername()
    print("ip:", peer[0], peer[1])
    q.d()


def test_https():
    from requests_toolbelt.adapters import host_header_ssl
    import socket

    cache_func = urllib3.util.connection.create_connection
    def wrap_create_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, socket_options=None):

        address = ("14.215.56.238", "443")
        return cache_func(address, timeout, source_address, socket_options)

    urllib3.util.connection.create_connection = wrap_create_connection

    s = requests.Session()
    s.mount("https://", host_header_ssl.HostHeaderSSLAdapter())
    res = s.get(
        "https://file3.data.weipan.cn/84687038/33aa2de11a520c616796445637c52edf13b9a17f?ip=1575539119,59.42.106.170&ssig=Djju4kRf0E&Expires=1575539719&KID=sae,l30zoo1wmz&fn=%E5%91%A8%E6%9D%B0%E4%BC%A6+-+%E4%B8%83%E9%87%8C%E9%A6%99.mp3&se_ip_debug=59.42.106.170&from=1221134",
        headers={"Host": "file3.data.weipan.cn"},
        stream=True,
        # verify=False,
    )
    content = res.raw.read(44)
    print(content)

    exit(1)
    with requests.Session() as s:
        s = requests.Session()
        s.mount("https://", host_header_ssl.HostHeaderSSLAdapter())
        # res = s.get("http://202.104.186.233:443/84687038/33aa2de11a520c616796445637c52edf13b9a17f?ip=1575535072,59.42.106.170&ssig=9xRrS2tbWs&Expires=1575535672&KID=sae,l30zoo1wmz&fn=%E5%91%A8%E6%9D%B0%E4%BC%A6+-+%E4%B8%83%E9%87%8C%E9%A6%99.mp3&se_ip_debug=59.42.106.170&from=1221134", headers={"Host": "file3.data.weipan.cn"}, stream=True)
        res = s.get("http://ayiis.me/aydocs/download/ex.zip", headers={"Host": "ayiis.me"}, stream=True)
        # res = s.get("https://113.113.73.32/5aV1bjqh_Q23odCf/static/superman/img/logo/bd_logo1_31bdc765.png", headers={"Host": "ss0.bdstatic.com"}, stream=True)
        # res = requests.get(
        #     "https://113.113.73.32/5aV1bjqh_Q23odCf/static/superman/img/logo/bd_logo1_31bdc765.png",
        #     timeout=(3, 3),
        #     headers={
        #         "Host": "ss0.bdstatic.com",
        #     },
        #     stream=True,
        # )
        print(111111111111)
        content = res.raw.read()     # only about content
        print("headers:", res.headers)
        open("akufwigf1b222.png", "wb").write(content)


def test_bar():
    from progress.spinner import Spinner
    Spinner.phases = ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛']
    _status_bar = Spinner("Downloading.. ", end="www")
    for i in range(100):
        time.sleep(0.02)
        _status_bar.next()
        _status_bar.message
    _status_bar.finish()


def test_bar2():
    from tqdm import tqdm
    import time
    pbar = tqdm(total=100)
    for i in range(10):
        time.sleep(0.1)
        pbar.update(10)
    pbar.close()


def test_dns():
    import dns.resolver

    # target_site = "img2018.cnblogs.com"
    target_site = "www.baidu.com"

    answers = dns.resolver.query(target_site)
    list1 = [str(a) for a in answers]

    dns_result = socket.getaddrinfo(target_site, 0, 0, 0, 0)
    list2 = list(set([z[-1][0] for z in dns_result]))

    # assert list1 == list(set(list1)), "dns.resolver is bad"
    # assert list2 == list(set(list2)), "socket.getaddrinfo is bad"
    assert set(list1) == set(list2), "list1 != list2"


if __name__ == "__main__":

    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    # test_bar()
    # test_bar2()

    # test_dns()

    # test_https()
    # test_stream()
    # test_session()
    main()
