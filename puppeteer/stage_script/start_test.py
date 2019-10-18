import q
import os
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


def wrap_test(func):
    def do(script_name):
        try:
            ts = time.time()
            re = exec_command("node %s" % script_name)

            func(re)
        except Exception as e:
            print("[FAILED] %ss %s: %s" % (round(time.time() - ts, 2), script_name, e))
        else:
            print("[PASS]  %ss %s" % (round(time.time() - ts, 2), script_name))

    return do


def basic_test():

    @wrap_test
    def test_hello_world(re):
        assert not re, "FAILED: %s" % re
        with open("helloworld.png", "rb") as rf:
            data = rf.read(8)
            data = data.decode("ISO-8859-1")
            assert "PNG" in data, "Not a PNG file."
        os.remove("helloworld.png")

    test_hello_world("test_hello_world.js")

    @wrap_test
    def test_save_as_pdf(re):
        assert not re, "FAILED: %s" % re
        with open("test_save_as_pdf.pdf", "rb") as rf:
            data = rf.read(300)
            data = data.decode("ISO-8859-1")
            assert any([True for x in range(5) if get_strftime_minus(-60 * 60 * 8 - x) in data]), "Date not valid."

        os.remove("test_save_as_pdf.pdf")

    test_save_as_pdf("test_save_as_pdf.js")


def main():
    basic_test()


if __name__ == "__main__":
    main()
