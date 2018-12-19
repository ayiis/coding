#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    结论： yield的所有Future获得result后立即返回
    yield gen.sleep(60)

"""


# 等待yield的所有Future返回

from tornado import gen
from tornado import ioloop
from tornado.concurrent import Future


@gen.coroutine
def main():
    print 'In main()'
    result = yield future_list
    print 'After all "Future"s return results:\r\n\t', result


def set_future_result():
    print 'Setting results of "Future"'
    future_list['val'].set_result('"Future" result val')
    for future in future_list['list']:
        future.set_result('"Future" result list ' + str(future_list['list'].index(future)))


def stop_ioloop(ioloop):
    print 'Stop ioloop'
    ioloop.stop()


future_list = {
    'val': Future(),
    'list': [Future(), Future()]
}


if __name__ == '__main__':
    main()
    iolooop = ioloop.IOLoop.current()
    iolooop.add_timeout(iolooop.time() + 1, lambda: set_future_result())
    iolooop.add_timeout(iolooop.time() + 2, lambda: stop_ioloop(iolooop))
    iolooop.start()
    print 'After ioloop stop.'


# 正确例子: 等待result的Future, 通过ioloop获取result
@gen.coroutine
def main():
    print 'In main()'
    # future.set_result('"Future" result val')
    iolooop.add_timeout(iolooop.time() + 1, lambda: future.set_result('"Future" result val'))
    result = yield future
    print 'After all "Future"s return results:\r\n\t', result


future = Future()
iolooop = ioloop.IOLoop.current()

if __name__ == '__main__':
    main()
    iolooop.add_timeout(iolooop.time() + 2, lambda: iolooop.stop())
    iolooop.start()
    print 'After ioloop stop.'


# 错误例子: 立即返回result的Future, 不会通过ioloop
@gen.coroutine
def main():
    print 'In main()'
    future.set_result('"Future" result val')
    # iolooop.add_timeout(iolooop.time() + 1, lambda: future.set_result('"Future" result val'))
    result = yield future
    print 'After all "Future"s return results:\r\n\t', result


future = Future()
iolooop = ioloop.IOLoop.current()

if __name__ == '__main__':
    main()
    iolooop.add_timeout(iolooop.time() + 2, lambda: iolooop.stop())
    iolooop.start()
    print 'After ioloop stop.'


