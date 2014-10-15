#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

MEMO = """
/ProjectA/TaskA/step1
hogehoge

/ProjectA/TaskA/step1
fugafuga
"""

from lib.core.Manager import Manager
from lib.ui.Journal import Journal

if __name__ == '__main__':
    ret = Manager.parse_memo(MEMO, Journal.path_reg)
    print(ret)
    pass
