#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import sys, os, datetime, time, configparser

from lib.core.Tasktory import Tasktory

if __name__ == '__main__':
    date = datetime.date.today().toordinal()
    root = Tasktory('', date + 365)

    _root = Tasktory('', date + 365)
    _proj = Tasktory('Project', date + 60)
    _task = Tasktory('Task', date + 30)
    _root.append(_proj)
    _proj.append(_task)

    t = root + _root

    for node in t:
        print(node.name, node.path(), [c.name for c in node.children],
                'None' if node.parent is None else node.parent.name)
