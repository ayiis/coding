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
        self.ts_counter = {
            "total_size": 0,
        }

    def touch_status_bar(self, chunk_size=1):
        # self.index / self.max
        try:
            self.lock.acquire()

            prev_size = self._status_bar.index - self.ts_counter["total_size"]
            ts = int(self._status_bar._ts)
            self.ts_counter[ts] = self.ts_counter.get(ts, 0) + prev_size
            if self.ts_counter.get(ts - 6):
                del self.ts_counter[ts - 6]

            self.ts_counter["total_size"] = self._status_bar.index

            total_ts = 0
            total_size = 0
            ts = int(self._status_bar._ts)
            for i in range(ts, ts - 6, -1):
                if i in self.ts_counter:
                    total_size += self.ts_counter[i]
                    total_ts += 1

            self.speed = " %s/s" % pretty_file_size(total_size * chunk_size / max(total_ts, 1))

            self._status_bar.next()
        finally:
            self.lock.release()

    def set_message(self, message):
        self._status_bar.message = message

    def clear_spin(self):
        self._status_bar.phases = [""]

    def finish_status_bar(self):
        self._status_bar.finish()

    def update(self, raw_bar):
        filled_length = int(raw_bar.width * raw_bar.progress)
        empty_length = raw_bar.width - filled_length
        message = raw_bar.message % raw_bar
        bar = raw_bar.fill * filled_length
        empty = raw_bar.empty_fill * empty_length
        suffix = raw_bar.suffix % raw_bar

        line = ''.join([message, raw_bar.bar_prefix, bar, empty, raw_bar.bar_suffix, suffix, ' ', self.speed])
        raw_bar.writeln(line)


class StatusBar(BaseStatus):
    """
        用于多线程下载：显示下载进度，递进式
    """
    def __init__(self, arg, total=0):
        super(StatusBar, self).__init__()
        self.arg = arg
        self._status_bar = Bar("Download status:", fill="█", max=total, suffix="%(percent)d%%")
        self._status_bar.update = lambda: self.update(self._status_bar)

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
            self.arg.touch_download_speed(0)
            self.touch_bar()
            time.sleep(0.2)

        self.end_bar()
