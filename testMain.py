#!python3
#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

from lib.core.Tasktory import Tasktory
#from lib.ui.Report import Report
from lib.ui.reports.report.sample import report

import datetime

if __name__ == '__main__':
    today = datetime.date.today()

    task = Tasktory('root', 1)
    task.append(Tasktory('t1', 1))
    task.append(Tasktory('t2', 1))
    task.append(Tasktory('t3', 1))

    pass
