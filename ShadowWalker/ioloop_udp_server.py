#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    基于 tornado 的 ioloop 的 UDPServer
"""
import socket
from tornado import ioloop

MAX_UDP_SIZE = 65507


class UDPServer(object):

    def __init__(self, address, port):
        self.io_loop = ioloop.IOLoop.current()
        self.address = address
        self.port = port

    def start(self):
        self.sock = self.bind_sockets(self.address, self.port)
        self.io_loop.add_handler(self.sock.fileno(), self.accept_handler, ioloop.IOLoop.READ)

    def bind_sockets(self, address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind((address, port))

        return sock

    def stop(self):
        self.io_loop.remove_handler(self.sock.fileno())
        self.sock.close()

    def accept_handler(self, fd, events):
        chunk, address = self.sock.recvfrom(MAX_UDP_SIZE)
        self.api_callback(chunk, address)

    def api_callback(self, chunk, address):
        print address, chunk

    def write(self, chunk, address):
        return self.sock.sendto(chunk, address)


#
#   TEST
#
from datetime import datetime


def do_with_chunk(chunk, address):
    print "do_with_chunk: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), chunk, address


def do_echo(udp_server):
    print "write len:", udp_server.write("~" * (datetime.now().second % 10), ("127.0.0.1", 8089))


def main():
    udp_server = UDPServer("0.0.0.0", 8089)
    udp_server.api_callback = do_with_chunk
    udp_server.start()
    ioloop.PeriodicCallback(lambda: do_echo(udp_server), 1 * 1000).start()


if __name__ == "__main__":
    main()
    ioloop.IOLoop.current().start()
