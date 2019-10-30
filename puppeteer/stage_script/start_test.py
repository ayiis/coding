import q
import os
import re
import subprocess
import time

SCRIPT_DIR = "stage_script"


def exec_command(cmd):

    result = os.popen(cmd)
    res = result.read()
    return os.linesep.join(res.splitlines())


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
    def do(script_name):
        try:
            ts = time.time()
            result = exec_command("node %s" % script_name)

            func(result)
        except Exception as e:
            print("[FAILED] %ss %s: %s" % (round(time.time() - ts, 2), script_name, e))
        else:
            print("[PASS]  %ss %s" % (round(time.time() - ts, 2), script_name))

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


def main():

    # basic_test()

    @wrap_test
    def test_take_screen_shot(result):
        assert not result, "FAILED: %s" % result
        with open("full.png", "rb") as rf:
            data = rf.read(8)
            data = data.decode("ISO-8859-1")
            assert "PNG" in data, "Not a PNG file."
        os.remove("full.png")

    test_take_screen_shot("test_take_screenshot.js")


if __name__ == "__main__":
    main()
