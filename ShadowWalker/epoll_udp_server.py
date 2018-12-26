#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    基于 epoll 的 UDPServer
"""
import sys
import traceback
import socket, select

reload(sys).setdefaultencoding("utf8")

MAX_UDP_SIZE = 65507


class EpollUDPServer(object):
    def __init__(self, addr, port):
        self.sock = self.init_sock(addr, port)
        self.epoll = select.epoll()
        self.epoll.register(self.sock.fileno(), select.EPOLLIN)

    def init_sock(self, addr, port):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind((addr, port))
        serversocket.setblocking(0)

        return serversocket

    def listen(self):
        while True:
            events = self.epoll.poll(-1)      # non -1 means without blocking
            for fileno, event in events:
                if fileno == self.sock.fileno():
                    try:
                        chunk, address = self.sock.recvfrom(MAX_UDP_SIZE)
                    except Exception:
                        print traceback.format_exc()

                    try:
                        self.api_callback(chunk, address)
                    except Exception:
                        print traceback.format_exc()
                else:
                    print "Error: got invalid fileno:", fileno, "on event:", events

    def stop(self):
        self.epoll.unregister(self.sock.fileno())
        self.epoll.close()
        self.sock.close()

    def api_callback(self):
        raise NotImplementedError()


#
#   TEST
#
import time


def do_with_chunk(chunk, address):
    print "do_with_chunk: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), chunk, address


def main():
    udp_server = EpollUDPServer("0.0.0.0", 8089)
    udp_server.api_callback = do_with_chunk
    udp_server.listen()


if __name__ == "__main__":
    main()
