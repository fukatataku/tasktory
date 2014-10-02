#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

from multiprocessing import Process, Pipe
from lib.monitor.monitor import dir_monitor
from lib.monitor.monitor import file_monitor

if __name__ == '__main__':
    dirpath = 'C:/home/fukata/tmp/fuga'
    filepath = 'C:/home/fukata/tmp/hoge.txt'
    conn1, conn2 = Pipe()
    p1 = Process(target=dir_monitor,
            name='TasktoryMonitor',
            args=(dirpath, conn2, 0))
    p2 = Process(target=file_monitor,
            name='JournalMonitor',
            args=(filepath, conn2, 1))

    p1.start()
    p2.start()
    try:
        while True:
            ret = conn1.recv()
            print(ret)
    finally:
        p1.terminate()
        p2.terminate()
    pass
