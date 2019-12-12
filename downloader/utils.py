import time
import urllib3
from progress.bar import Bar
from progress.spinner import Spinner
import threading

KB = 1024


def pretty_file_size(byte):
    """
        格式化文件尺寸 最小是B，最大是T
    """
    size = ["B", "K", "M", "G", "T"]
    i = 0
    res = byte
    while 999 < res:
        res = res / KB
        i = i + 1
        if i == len(size) - 1:
            break

    return "%s%s" % (round(res, 2), size[i])


class ConnectPatch(object):

    def __init__(self, addr_list):
        self.setting = {
            "_create_connection": None,
            "addr_list": list(set(addr_list)),
            "addr_counter": 0,
        }

    def next_connect_patch(self):
        if self.setting["addr_counter"] == len(self.setting["addr_list"]) - 1:
            self.setting["addr_counter"] = 0
        else:
            self.setting["addr_counter"] += 1

    def wrap_create_connection(self, address, *argc, **argv):
        new_address = (
            self.setting["addr_list"][self.setting["addr_counter"]],
            address[1]
        )
        # print("new_address: %s -> %s" % (address, new_address))
        self.next_connect_patch()
        return self.setting["_create_connection"](new_address, *argc, **argv)

    def patch(self):
        print("Host list:", self.setting["addr_list"])
        self.setting["_create_connection"] = urllib3.util.connection.create_connection
        urllib3.util.connection.create_connection = self.wrap_create_connection

    def finish(self):
        urllib3.util.connection.create_connection = self.setting["_create_connection"]


class BaseStatus(object):

    def __init__(self):
        self.lock = threading.Lock()

    def touch_status_bar(self):
        try:
            self.lock.acquire()
            self._status_bar.next()
        finally:
            self.lock.release()

    def set_message(self, message):
        self._status_bar.message = message

    def clear_spin(self):
        self._status_bar.phases = [""]

    def finish_status_bar(self):
        self._status_bar.finish()


class StatusBar(BaseStatus):
    """
        用于多线程下载：显示下载进度，递进式
    """
    def __init__(self, arg, total=0):
        super(StatusBar, self).__init__()
        self.arg = arg
        self._status_bar = Bar("Download status:", fill="█", max=total, suffix="%(percent)d%%")

    def start():
        pass


class StatusSpinner(BaseStatus):
    """
        用于单线程下载：显示下载进度，固定式
    """
    def __init__(self, arg):
        super(StatusSpinner, self).__init__()
        self.arg = arg
        self.total_size = 0
        self.download_finished = False

    def finish_download(self):
        self.download_finished = True

    def touch_bar(self):
        self._status_bar.message = "Got: %s, Speed: %s/s " % (
            pretty_file_size(self.total_size),
            self.arg.get_download_speed()
        )
        self._status_bar.message = self._status_bar.message.ljust(36, " ")
        self.touch_status_bar()

    def end_bar(self):
        self.clear_spin()
        ts_s = round(time.time() - self.init_ts, 2)
        message = "Total Size: %s, Total Time: %ss, Avg Speed: %s/s " % (
            pretty_file_size(self.total_size),
            ts_s,
            pretty_file_size(self.total_size / max(ts_s, 1)),
        )
        message = message.ljust(49, " ")
        self.set_message(message)
        self.touch_status_bar()
        self.finish_status_bar()
        print("Done.")

    def start(self):
        Spinner.phases = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
        self._status_bar = Spinner("Init downloader.. ")
        self.touch_status_bar()

        while not self.download_finished:
            self.touch_bar()
            time.sleep(0.2)

        self.end_bar()
