#!python3
#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

from lib.core.Tasktory import Tasktory
from lib.ui.Report import Report

import datetime

if __name__ == '__main__':
    today = datetime.date(2014, 9, 24)
    timestamp = datetime.datetime(2014, 9, 20, 9, 0, 0).timestamp()

    task = Tasktory('Tasktory', 1)
    task.append(Tasktory('make_report.py', 1, Tasktory.CLOSE).add_time(timestamp, 1800))
    task.append(Tasktory('test_report.py', 1).add_time(timestamp+1800, 3600))
    task.append(Tasktory('test_manager.py', 1))

    for name, text in Report.report_all(today, task):
        print('====')
        print(name)
        print('====')
        print(text)
        print('')

    pass
