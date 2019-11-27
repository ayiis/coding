import q
import os
# import signal
import subprocess
import traceback
import multiprocessing
import re
import time

SCRIPT_DIR = "stage_script"


def exec_command(cmd):

    result = os.popen(cmd)
    res = result.read()
    return os.linesep.join(res.splitlines())


def empty_queue(qq):

    while not qq.empty():
        qq.get()


class ProcessThing(multiprocessing.Process):
    """
        you are not communicating with the subprocess
    """
    def __init__(self, arg):
        super(ProcessThing, self).__init__()
        self.in_queue = arg["in_queue"]
        self.out_queue = arg["out_queue"]
        self.exit = multiprocessing.Event()

    def run(self):
        try:
            while True:

                # break multiprocessing if exit
                if self.exit.is_set():
                    break

                if not self.in_queue.empty():
                    data = self.in_queue.get()
                    # when leave `with` statement, proc will be kill
                    # redirect stderr > subprocess.STDOUT
                    with subprocess.Popen(data["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1) as proc:
                        for line in iter(proc.stdout.readline, b""):
                            # break subprocess if exit
                            if self.exit.is_set():
                                break
                            else:
                                self.out_queue.put({"out": line.decode("utf8")})

                time.sleep(0.1)

        except Exception:
            print(traceback.format_exc())

        finally:
            try:
                empty_queue(self.in_queue)
                empty_queue(self.out_queue)
            except Exception:
                print(traceback.format_exc())


def new_multiprocess():

    args = {
        "in_queue": multiprocessing.Queue(),
        "out_queue": multiprocessing.Queue(),
    }

    args["proc"] = ProcessThing(args)
    args["proc"].start()

    return args


def get_timestamp():
    return int(time.time() * 1000)


def get_strftime_minus(lt):
    return time.strftime("%Y%m%d%H%M%S", time.localtime(time.time() + lt))


def assert_time_in_string(data_string, fixed=0):
    for x in range(6):
        now_ts = get_strftime_minus(-1 * 60 * 60 * fixed - x + 1)
        if now_ts in data_string:
            return None
    else:
        raise Exception("Date not valid.")


def wrap_test(func):
    def do(script_name, extra_para=""):
        try:
            ts = time.time()
            result = exec_command("node %s %s" % (script_name, extra_para))

            print_text = func(result)
        except Exception as e:
            print("[❌ FAILED] %ss %s: %s" % (round(time.time() - ts, 2), script_name, e))
        else:
            print("[✅ PASS]  %ss %s %s" % (round(time.time() - ts, 2), script_name, print_text))

    return do


def basic_test():

    @wrap_test
    def test_hello_world(result):
        assert not result, "FAILED: %s" % result
        with open("helloworld.png", "rb") as rf:
            data = rf.read(8)
            data = data.decode("ISO-8859-1")
            assert "PNG" in data, "Not a PNG file."
        os.remove("helloworld.png")

    test_hello_world("test_hello_world.js")

    @wrap_test
    def test_save_as_pdf(result):
        assert not result, "FAILED: %s" % result
        with open("test_save_as_pdf.pdf", "rb") as rf:
            data = rf.read(300)
            data = data.decode("ISO-8859-1")
            assert_time_in_string(data, fixed=+8)

        os.remove("test_save_as_pdf.pdf")

    test_save_as_pdf("test_save_as_pdf.js")

    @wrap_test
    def test_get_dimensions(result):
        assert "{ width: 800, height: 600, deviceScaleFactor: 1 }" in result, "FAILED: %s" % result

    test_get_dimensions("test_get_dimensions.js")

    @wrap_test
    def test_search(result):
        # print("result:", result)
        assert_time_in_string(result)

    test_search("test_search.js")

    @wrap_test
    def test_right_click(result):
        """
            YOU CAN DO NOTHING FOR NOW
        """
        print("result:", result)

    @wrap_test
    def test_two_page(result):
        # print("result:", result)
        assert_time_in_string(result)

    test_two_page("test_two_page.js")

    @wrap_test
    def test_grep_link(result):
        assert "10" == result, "Link count not right"

    test_grep_link("test_grep_link.js")

    @wrap_test
    def test_block_something(result):
        assert re.match(r"^net::ERR_FAILED", result), "Site block failed"

    test_block_something("test_block_something.js")

    @wrap_test
    def test_download_file(result):
        assert re.match(r"/tmp/[a-z0-9\-]*/inst.exe$", result), "File download failed"
        os.remove(result)

    test_download_file("test_download_file.js")

    @wrap_test
    def test_execute_before_load(result):
        assert result == "Sniffed: true", "execute failed"

    test_execute_before_load("test_execute_before_load.js")

    @wrap_test
    def test_use_chrome(result):
        # print("result:", result)
        assert_time_in_string(result)

    test_use_chrome("test_use_chrome.js")

    @wrap_test
    def test_use_proxy(result):
        # print("result:", result)
        assert result == "https://github.com/GoogleChrome/puppeteer", "proxy result is bad"

    test_use_proxy("test_use_proxy.js")

    @wrap_test
    def test_take_screenshot(result):
        assert not result, "FAILED: %s" % result
        with open("full.png", "rb") as rf:
            data = rf.read(8)
            data = data.decode("ISO-8859-1")
            assert "PNG" in data, "Not a PNG file."
        os.remove("full.png")

    test_take_screenshot("test_take_screenshot.js")

    @wrap_test
    def test_wait_for(result):
        assert result == "我想要的一切", "即将来临"
        return result

    test_wait_for("test_wait_for.js")

    @wrap_test
    def test_use_this_page(result):
        assert not result, result

    test_use_this_page("test_use_this_page.js")

    # exec_command(""""/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9999 --no-first-run --no-default-browser-check --user-data-dir=/tmp/tmp""")
    new_or_existing_chrome()    # first run will open a browser
    new_or_existing_chrome()    # second run will use the last browser && then close it


def new_or_existing_chrome():
    tt = new_multiprocess()
    tt["in_queue"].put({
        "cmd": [
            "/mine/soft/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--remote-debugging-port=9999",
            "--no-first-run",
            "--no-default-browser-check",
            "--user-data-dir=/tmp/tmp",
            "https://www.baidu.com/",
        ],
    })
    close = 0
    ws_debug_url = ""
    while True:
        res = tt["out_queue"].get()
        if "DevTools listening on" in res.get("out", ""):
            close = 0
            ws_debug_url = res["out"].replace("DevTools listening on", "").strip()
            break
        if "Opening in existing browser session" in res.get("out", ""):
            close = 1
            import requests
            for i in range(5):
                try:
                    res = requests.get("http://127.0.0.1:9999/json/version", timeout=5)
                    json_data = res.json()
                    ws_debug_url = json_data["webSocketDebuggerUrl"]
                except Exception:
                    print(traceback.format_exc())

            if ws_debug_url:
                break

    # print("ws_debug_url:", ws_debug_url)

    @wrap_test
    def test_new_or_existing_chrome(result):
        assert result == "pass", "Go try catch something."
        tt["proc"].exit.set()
        # tt["proc"].join()
        tt["proc"].kill()   # wait for no time
        return close and "关闭上一个浏览器" or "新开一个浏览器"

    test_new_or_existing_chrome(
        "test_new_or_existing_chrome.js",
        "-c %s -t %s -w %s" % (close, "百度一下", ws_debug_url),
    )


def main():

    # basic_test()
    # return

    new_or_existing_chrome()
    new_or_existing_chrome()

    # @wrap_test
    # def test_use_this_page(result):
    #     assert not result, result
    # test_use_this_page("test_use_this_page.js")


if __name__ == "__main__":
    main()
