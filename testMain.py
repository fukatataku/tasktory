#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

from lib.core.Tasktory import Tasktory

if __name__ == '__main__':
    t1 = Tasktory(1, '1', 10)
    t11 = Tasktory(2, '1-1', 11)
    t12 = Tasktory(3, '1-2', 11)
    t121 = Tasktory(4, '1-2-1', 10)
    t13 = Tasktory(5, '1-3', 11)
    t12.append(t121)
    t1.append(t11)
    t1.append(t12)
    t1.append(t13)
    for t in t1:
        print("{}{}".format('*'*t.level(), t.name))
    pass
