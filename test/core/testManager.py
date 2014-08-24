#!/usr/bin/env python3
#-*- encoding:utf-8 -*-

import sys, os
import datetime
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
append_path = lambda p:sys.path.append(os.path.join(THIS_DIR, p))
append_path('../../lib/core')

from Tasktory import Tasktory
from Manager import Manager

class TestTasktory(unittest.TestCase):

    def test_get(self):
        pass

    def test_put(self):
        pass

    def test_get_tree(self):
        pass

    def test_put_tree(self):
        pass

    def test_commit(self):
        pass

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
