#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

from lib.core.Tasktory2 import Tasktory

import datetime

if __name__ == '__main__':
    task = Tasktory('root', 1)
    task.append(Tasktory('t1', 1))
    task.append(Tasktory('t2', 1))
    task.append(Tasktory('t3', 1))

    print(task.name)
    t, p = task.find('/root')
    print(t.name if t else t, p)

    pass
