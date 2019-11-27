import q
import os
import signal
import traceback
import subprocess
import multiprocessing
import re
import time


class ThreadThing(multiprocessing.Process):
    def __init__(self, arg):
        super(ThreadThing, self).__init__()
        self.in_queue = arg["in_queue"]
        self.out_queue = arg["out_queue"]
        self.killm = multiprocessing.Event()

    def run(self):
        # for i in range(40):
        #     self.out_queue.put({"data": "0123456789" * 100})

        # print("kill!", dir(self.out_queue))
        # print("self.out_queue:", self.out_queue.full())
        # empty_queue(self.out_queue)
        # print("self.out_queue:", self.out_queue.qsize())

        with subprocess.Popen("top", stdout=subprocess.PIPE, bufsize=1) as proc:
            for line in iter(proc.stdout.readline, b""):
                if self.killm.is_set():
                    print("killing 1!")
                    break
                else:
                    self.out_queue.put({"data": line.decode("utf8")})

            proc.stdout.close()
            proc.wait()
            # proc.kill()

        print("qqqqqq 5")
        empty_queue(self.out_queue)
        print("qqqqqq 6")

    def run00(self):
        try:
            with os.popen("top") as proc:
                while True:
                    line = proc.readline()
                    if self.killm.is_set():
                        proc.close()
                        empty_queue(self.out_queue)
                        empty_queue(self.in_queue)
                        break
                    elif line:
                        if self.out_queue.full():
                            print("FUCKED")
                        else:
                            self.out_queue.put({"data": line})

        except Exception:
            print(traceback.format_exc())

        print("q5")
        return 1


def empty_queue(qq):
    ic = 0
    while not qq.empty():
        qq.get()
        ic += 1
    print("fucked done:", ic)


def main():

    in_queue = multiprocessing.Queue()
    out_queue = multiprocessing.Queue()

    tt = ThreadThing({
        "in_queue": in_queue,
        "out_queue": out_queue,
    })

    tt.start()

    print("zzzzzzzzzz. 0")

    time.sleep(2)

    tt.killm.set()

    tt.join()

    print("zzzzzzzzzz. 1")

    exit(1)


if __name__ == "__main__":
    # import queue

    # qq = queue.Queue()

    # for i in range(978):
    #     qq.put(1)

    # print(qq.qsize())
    # print(qq.empty())
    # empty_queue(qq)
    # print(qq.qsize())
    # print(qq.empty())
    # # q.d()

    # # print(dir(qq))

    # exit(1)
    main()
