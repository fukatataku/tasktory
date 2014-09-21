#!python3
#-*- encoding:utf-8 -*-

import sys, os, datetime, unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager

class TestTasktory(unittest.TestCase):

    def test_(self):
        pass

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
