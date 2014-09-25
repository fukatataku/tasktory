#!python3
#-*- encoding:utf-8 -*-

import sys, os, datetime, unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager

ROOT = '/Users/taku/tmp/work'

class TestManager(unittest.TestCase):

    def check(self, task, name, deadline, parent, status, category, comments):
        self.assertEqual(task.name, name)
        self.assertEqual(task.deadline, deadline)
        self.assertIs(task.parent, parent)
        self.assertEqual(task.status, status)
        self.assertEqual(task.category, category)
        self.assertEqual(task.comments, comments)
        return

    def check_child(self, task, *children):
        self.assertListEqual(
                sorted(task.children, key=lambda t:t.ID),
                sorted(children, key=lambda t:t.ID)
                )
        return

    def check_time(self, task, *timetable):
        self.assertListEqual(
                sorted(task.timetable, key=lambda t:t[0]),
                sorted(timetable, key=lambda t:t[0])
                )
        return

    @classmethod
    def setUpClass(cls):
        return

    @classmethod
    def tearDownClass(cls):
        return

    def setUp(self):
        return

    def tearDown(self):
        # self\.t.*[0-9] を削除する
        names = [n for n in dir(self)
                if n[0] == 't' and n[-1] in '1234567890' and '_' not in n]
        cmds = ["del self.{}".format(n) for n in names]
        for cmd in cmds: exec(cmd)

        # ROOT以下のディレクトリ、ファイルを一掃する
        return

    def test_get_tree(self):
        return

    def test_get(self):
        # 空タスクトリをputしてからgetする
        return

    def test_put(self):
        # getと一緒にテストする
        return

    def test_overlap(self):
        return

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
