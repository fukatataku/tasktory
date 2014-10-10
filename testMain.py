#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

from lib.core.Manager import Manager
from lib.ui.Journal import Journal

MEMO = """

HOGEHOGE

/Project/TaskA/step1



ABCDE

FGHIJ
KKKKK

/Project/TaskA/step2
AAAA


BBBB
CCCC
"""

if __name__ == '__main__':
    d = Journal.parse_memo(MEMO)
    for key, value in d.items():
        print('===', key, '===')
        print(Manager.delete_blank(value))
    pass
