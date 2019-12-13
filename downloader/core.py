import q
import re
import math
import time
import queue
import socket
import urllib3
import threading
import traceback

import utils

import requests

READ_CHUNK_SIZE = requests.models.CONTENT_CHUNK_SIZE or (10 * 1024)
MAX_TRUNK_SIZE = READ_CHUNK_SIZE * 1024


class SingleThreadDownloader(object):
    """
        单线程下载，用于不支持多线程下载的文件
    """
    def __init__(self, arg):
        super(SingleThreadDownloader, self).__init__()
        self.arg = arg

    def write_file(self, content):
        self.fd.write(content)

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

        return utils.pretty_file_size(total_size / max(total_ts, 1))

    def touch_download_speed(self, chunk_size):
        """
            存储并返回前5秒的平均下载速度
            在 get_download_speed 计算
        """
        if not hasattr(self, "init_ts"):
            self.init_ts = time.time()
            self.bar.init_ts = self.init_ts
            self.ts_counter = {
                "total_size": 0
            }

        ts_counter = self.ts_counter

        self.now_ts_s = int(time.time() - self.init_ts)
        ts_counter[self.now_ts_s] = ts_counter.get(self.now_ts_s, 0) + chunk_size
        ts_counter["total_size"] += chunk_size

        if ts_counter.get(self.now_ts_s - 6):
            del ts_counter[self.now_ts_s - 6]

        self.bar.total_size = ts_counter["total_size"]

    def run(self):

        self.bar = utils.StatusSpinner(self)
        self.touch_download_speed(0)
        thread = threading.Thread(target=self.bar.start, args=())
        thread.start()

        self.fd = open(self.arg.file_name, "wb+")
        with requests.Session() as session:
            res = session.get(
                self.arg.target_url,
                headers={
                    "Accept-Encoding": "*",
                    "Referer": self.arg.target_url,
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

        self.bar.finish_download()
        thread.join()
        self.fd.close()


class MultiThreadDownloader(object):
    """
        多线程下载，使用range实现分段下载
    """
    def __init__(self, arg):
        super(MultiThreadDownloader, self).__init__()
        self.arg = arg
        self.task_queue = queue.Queue()
        self.task_finish_count = 0
        self.task_total_count = 0
        self.lock = threading.Lock()
        self.lock2 = threading.Lock()
        self.lock_file = threading.Lock()
        self.fail_times = 0
        self.download_finished = False
        self.header_info_done = False
        self.dns_query_done = False

    def write_file(self, content, seek):
        """
            网速很快时，过于频繁的写入是否会有性能瓶颈？
        """
        try:
            self.lock_file.acquire()

            self.fd.seek(seek)
            self.fd.write(content)

        finally:
            self.lock_file.release()

    def split_task(self):
        """
            将任务切割成多份，根据线程数量切割
            10K <= 任务单位大小 <= 10M
        """
        if self.arg.file_size // READ_CHUNK_SIZE < self.arg.max_thread:
            package_count = math.ceil(self.arg.file_size / READ_CHUNK_SIZE)

        elif self.arg.max_thread * MAX_TRUNK_SIZE < self.arg.file_size:
            package_count = math.ceil(self.arg.file_size / MAX_TRUNK_SIZE)

        else:
            package_count = self.arg.max_thread

        base_package_size = self.arg.file_size // READ_CHUNK_SIZE
        package_padding = self.arg.file_size % READ_CHUNK_SIZE
        base_package_count = base_package_size // package_count
        base_package_padding = base_package_size % package_count

        start_size = 0
        for i in range(package_count):
            pad = base_package_padding > i and READ_CHUNK_SIZE or 0
            # pad to the last package
            if i == package_count - 1:
                pad += package_padding
            end_size = start_size + base_package_count * READ_CHUNK_SIZE + pad
            self.task_queue.put({
                "start": start_size,
                "end": min(end_size, self.arg.file_size),
            })
            start_size = end_size

        print(
            "package size:",
            utils.pretty_file_size(base_package_count * READ_CHUNK_SIZE + (base_package_padding > 0 and READ_CHUNK_SIZE or 0) + package_padding),
            "&& Q size:",
            self.task_queue.qsize()
        )
        self.task_total_count = self.task_queue.qsize()

    def fail_task(self, task):
        self.fail_times += 1
        print("[WARNING] Total fail: %s / %s" % (self.fail_times, self.task_total_count))

    def finish_task(self, task):

        try:
            self.lock2.acquire()

            self.task_finish_count += 1

            if self.task_finish_count == self.task_total_count:
                self.bar.finish_status_bar()

        finally:
            self.lock2.release()

    def get_next_task(self):
        """
            use lock to make sure
        """
        try:
            self.lock.acquire()

            task = None
            if not self.task_queue.empty():
                task = self.task_queue.get()

            return task

        finally:
            self.lock.release()

    def do_task(self):
        """
            核心代码，通过构造Range来分段获取文件内容
        """
        with requests.Session() as session:
            retry = False

            while True:

                if not retry:
                    task = self.get_next_task()
                    if task is None:
                        break

                try:

                    headers = {
                        # "Host": self.target_host,
                        # `start` <= Range <= `end`, So `end` should -1
                        "Range": "Bytes=%s-%s" % (task["start"], task["end"] - 1),
                        "Accept-Encoding": "*",
                        "Referer": self.arg.target_url,
                    }
                    res = session.get(
                        self.arg.target_url,
                        headers=headers,
                        timeout=(5, self.arg.chunk_timeout),
                        stream=True,
                    )

                    while True:

                        content = res.raw.read(READ_CHUNK_SIZE)     # no headers, only the content

                        self.write_file(content, task["start"])
                        self.bar.touch_status_bar()

                        if len(content) == task["end"] - task["start"]:
                            break

                        # DEBUG: never should this happened. `the above break` should works.
                        if len(content) < READ_CHUNK_SIZE:
                            raise Exception("[ERROR] Something is wrong.")

                        task["start"] = task["start"] + READ_CHUNK_SIZE

                except (urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
                    retry = True
                    self.fail_task(task)
                    time.sleep(0.2)

                except Exception:
                    print(traceback.format_exc())
                    retry = True
                    self.fail_task(task)
                    time.sleep(0.2)

                else:
                    retry = False
                    self.finish_task(task)

    def run(self):

        self.split_task()
        # 预先分配空间
        self.fd = open(self.arg.file_name, "wb+")
        self.write_file(b"\0", self.arg.file_size - 1)

        ts = time.time()
        print(
            "[⏱  START]",
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            "File size:", utils.pretty_file_size(self.arg.file_size),
        )
        print()

        max_count = math.ceil(self.arg.file_size / READ_CHUNK_SIZE)
        self.bar = utils.StatusBar(self, total=max_count)

        thread_list = []
        for i in range(self.arg.max_thread):

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
            "Avg speed: %s/s" % utils.pretty_file_size(self.arg.file_size / max(time.time() - ts, 1)),
        )


class DownloadBuilder(object):
    """
        通过发送range请求，探测适用于目标文件的下载方式
    """
    def __init__(self, arg):
        super(DownloadBuilder, self).__init__()
        self.arg = arg
        self.max_thread = arg.get("max_thread") or 8
        self.chunk_timeout = arg.get("chunk_timeout") or 8
        self.target_url = arg["target_url"]
        self.file_name = arg.get("file_name", None)
        self.target_host = re.match(r"http[s]?://([^/]+)", self.target_url).group(1)
        self.header_info_done = False
        self.dns_query_done = False
        self.file_size = 0
        self.addr_list = []

    def header_print(self, *argv):
        if self.header_info_done:
            return
        else:
            print(*argv)

    def dns_query_by_socket(self):

        for i in range(2):
            if self.dns_query_done:
                break
            try:
                dns_result = socket.getaddrinfo(self.target_host, 0, 0, 0, 0)
                self.addr_list = list(set([z[-1][0] for z in dns_result]))
                self.dns_query_done = True
            except Exception:
                if not self.dns_query_done:
                    self.header_print(traceback.format_exc())
                time.sleep(0.2)

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
                    timeout=self.chunk_timeout,
                    stream=True,
                )
                hcr = res.headers.get("Content-Range")

                peer = res.raw._fp.fp.raw._sock.getpeername()
                self.addr_list.append(peer[0])
                # self.header_print("Get host addr: %s -> %s:%s" % (self.target_host, peer[0], peer[1]))

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
        for i in range(2):
            thread = threading.Thread(target=self.dns_query_by_socket)
            thread.start()

        queue_out = queue.Queue()
        for i in range(2):
            thread = threading.Thread(target=self.get_header_info, args=(queue_out, ))
            thread.start()

        return queue_out.get()

    def single_thread_downloader(self):
        downloader = SingleThreadDownloader(self)
        downloader.run()

    def multi_thread_downloader(self):

        # 强制使用指定IP解析域名，提高速度
        self.connect_patch = utils.ConnectPatch(self.addr_list)
        self.connect_patch.patch()

        downloader = MultiThreadDownloader(self)
        downloader.run()

        self.connect_patch.finish()

    def start_task(self):

        # 获取文件尺寸，测试是否支持 range 方式（多线程，断点续传）
        ts = time.time()
        res = self.double_finger()
        self.header_info_done = True

        print("Get file info: %ss, save as %s" % (round(time.time() - ts, 3), self.file_name))

        if res <= 0:
            print("[WANRING] start single line downloader..")
            return self.single_thread_downloader()

        # 查 DNS，如果堵塞了，等待5秒（为了应对垃圾网络）
        for i in range(50):
            if not self.dns_query_done:
                time.sleep(0.1)

        return self.multi_thread_downloader()


if __name__ == "__main__":
    args = {
        "target_url": "https://ayiis.me/aydocs/readme.txt",
        "file_name": "ex.zip",
        "max_thread": None,
        "chunk_timeout": None,
    }
    db = DownloadBuilder(args)
    db.start_task()
