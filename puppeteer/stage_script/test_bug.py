import q
import os
# import signal
import subprocess
import multiprocessing
import re
import time


class ProcessThing(multiprocessing.Process):
    def __init__(self, in_queue, out_queue):
        super(ProcessThing, self).__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        print("123")
        cmd = self.in_queue.get()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1)
        res = "".join([x.decode("utf8") for x in iter(proc.stdout.readline, b"")])
        proc.stdout.close()
        print(dir(proc))
        print(proc.pid)
        proc.wait()
        # proc.join()
        proc.kill()
        self.out_queue.put(res)
        print("exiting proc...")


def main():

    in_queue = multiprocessing.Queue()
    out_queue = multiprocessing.Queue()
    pt = ProcessThing(in_queue, out_queue)
    in_queue.put("ps")
    pt.start()

    res = out_queue.get()
    print("res:", res)
    pt.join()


if __name__ == "__main__":
    main()
