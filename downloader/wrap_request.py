"""
    为了应对日益严重的 tcp 中断情况
"""
import q
import time
import traceback
import threading
import queue
import requests

KB = 1024
CHUNK_SIZE = (128 * KB)                     # 每个线程一次下载的大小 ?128KB
CHUNK_TIMEOUT = CHUNK_SIZE // (3 * KB)      # 每个线程一次下载速度最慢 ?3KB/s 超时
HEAD_TIMEOUT = CHUNK_SIZE // CHUNK_TIMEOUT // KB * 2 + 5  # 2: header视作2KB; 5: 适应值
THREAD_MAX = 8                             # 最大线程数量 ?8 个


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


class Wrapper(object):
    def __init__(self, arg):
        super(Wrapper, self).__init__()
        self.target_url = arg["target_url"]
        self.file_name = arg["file_name"]
        self.task_queue = queue.Queue()
        self.task_finish_count = 0
        self.task_total_count = 0
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
            self.task_queue.put({"start": tmp_size, "end": min(tmp_size + CHUNK_SIZE, self.file_size)})
            tmp_size = tmp_size + CHUNK_SIZE

        self.task_total_count = self.task_queue.qsize()

    def get_next_task(self):

        if self.task_queue.empty():
            return None

        return self.task_queue.get()

    def fail_task(self, task):
        self.task_queue.put(task)

    def finish_task(self, task):
        self.task_finish_count += 1
        print("done: %s-%s - %s%%" % (
            task["start"],
            task["end"],
            round(self.task_finish_count / self.task_total_count * 100, 2),
        ))

    def get_header_info(self):
        """
            发送一个 head 请求，获取内容总长度
        """
        res = requests.head(self.target_url, timeout=HEAD_TIMEOUT)
        self.file_size = int(res.headers["content-length"])

    def get_header_info_r(self, queue_out):
        """
            获取内容总长度 并验证是否支持 Range 方式下载
        """
        headers = {
            "Range": "Bytes=0-43",  # a wav header length is 44
            "Accept-Encoding": "*",
        }
        # 重试2次
        for i in range(2):
            try:
                res = requests.get(self.target_url, headers=headers, timeout=HEAD_TIMEOUT)
                hcr = res.headers.get("Content-Range")
                if not hcr:
                    raise Exception("Not suit for content-range.")

                self.file_size = int(hcr.split("/")[1])
                if not (len(res.content) == 44 and hcr == "bytes 0-43/%s" % (self.file_size)):
                    queue_out.put(0)
                    raise Exception("Len not good: %s" % len(res.content))
            except Exception:
                print(traceback.format_exc())
            else:
                queue_out.put(self.file_size)
                break

    def double_finger(self):
        """
            并发获取内容总长度, 通过 queue_out 通知主线程
        """
        queue_out = queue.Queue()
        thread_list = []

        for i in range(2):
            thread = threading.Thread(target=self.get_header_info_r, args=(queue_out, ))
            thread.start()
            thread_list.append(thread)

        # print("waiting...")
        res = queue_out.get()
        if res < 1:
            raise Exception("Not good.")

    def do_task(self):
        """
            1
        """
        while True:

            task = self.get_next_task()
            if task is None:
                # print("task done", "exit thread.")
                return None

            try:

                headers = {
                    # `start` <= Range <= `end`
                    # So `end` should -1
                    "Range": "Bytes=%s-%s" % (task["start"], task["end"] - 1),
                    "Accept-Encoding": "*",
                }
                res = requests.get(self.target_url, headers=headers, timeout=CHUNK_TIMEOUT)

                # print("%s-%s download success" % (task["start"], task["end"]))

                if len(res.content) != task["end"] - task["start"]:
                    print("Not suit: %s != %s ; from %s to %s" % (
                        len(res.content),
                        task["end"] - task["start"],
                        task["start"],
                        task["end"],
                    ))
                    raise Exception("Not suitable.")

                self.fd.seek(task["start"])
                self.fd.write(res.content)

            except Exception:
                print(traceback.format_exc())
                self.fail_task(task)

            else:
                self.finish_task(task)

    def start_task(self):

        ts = time.time()
        self.double_finger()
        self.split_task()
        print("Get file info: %ss, download chunk: %s" % (round(time.time() - ts, 3), self.task_queue.qsize()))

        # 预先分配空间
        self.fd = open(self.file_name, "wb+")
        self.fd.seek(self.file_size)
        self.fd.write(b"")

        ts = time.time()
        print(
            "[⏱ START]",
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            "File size:", pretty_file_size(self.file_size),
        )
        print()

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
            "Total time:", round(time.time() - ts, 3), "s",
            "Avg speed: %s/s" % pretty_file_size(self.file_size / max(time.time() - ts, 1)),
        )


def main():
    args = {
        # "target_url": "https://ayiis.me/",
        # "target_url": "https://ayiis.me/aydocs/download/ex.zip",
        "target_url": "http://war3down1.uuu9.com/war3/201911/201911251725.rar",
        # "target_url": "https://ss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/img/logo/bd_logo1_31bdc765.png",
        # "file_name": "baidu.png",
        "file_name": "201911251725.rar",
    }
    w = Wrapper(args)

    w.start_task()


if __name__ == "__main__":
    main()
