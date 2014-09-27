#!python3
#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

from lib.core.Tasktory import Tasktory
from lib.ui.Report import Report

import os, pickle, datetime

if __name__ == '__main__':
    task = Tasktory('hoge', 1)
    filepath = '/Users/taku/tmp'
    profile = os.path.join(filepath, '.tasktory')
    with open(profile, 'wb') as f:
        pickle.dump(task, f)
    pass
