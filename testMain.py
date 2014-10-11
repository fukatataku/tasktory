#!python3
#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import datetime

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


BBBBB
CCCC

/Project/TaskA/step3
あいうえお
かきくけこ
さしすせそ
たちつてと
"""

DIRPATH = '/Users/taku/tmp/test'
NAME = 'memo.txt'

put = lambda t: Manager.put_memo(datetime.datetime.now(), DIRPATH, t, NAME)
get = lambda: Manager.get_memo(DIRPATH, NAME)

if __name__ == '__main__':
    d = Journal.parse_memo(MEMO)

    memo_list = Journal.parse_memo(MEMO)
    #for path, text in memo_list:
        #print('===', path, '===')
        #print(text)
        #put(text)

    for path, memo in memo_list:
        memo = Manager.delete_blank(memo)
        if memo not in get():
            put(memo)
