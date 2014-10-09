#!python3
#-*- encoding:utf-8 -*-

import sys, os, shutil, datetime, unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager

OPEN = Tasktory.OPEN
WAIT = Tasktory.WAIT
CLOSE = Tasktory.CLOSE
CONST = Tasktory.CONST

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
        self.root = '/Users/taku/tmp/test/work'
        self.profile = '.tasktory'

        # ROOT以下のディレクトリ、ファイルを一掃する
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        return

    def tearDown(self):
        # self\.t.*[0-9] を削除する
        names = [n for n in dir(self)
                if n[0] == 't' and n[-1] in '1234567890' and '_' not in n]
        cmds = ["del self.{}".format(n) for n in names]
        for cmd in cmds: exec(cmd)

        # ROOT以下のディレクトリ、ファイルを一掃する
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        return

    #==========================================================================
    # get_tree
    #==========================================================================
    def test_get_tree(self):
        # 存在しないパス
        self.assertFalse(os.path.exists(self.root))
        self.assertIsNone(Manager.get_tree(self.root, self.profile))

        # タスクトリでないパス
        self.assertIsNone(Manager.get_tree('/Users/taku', self.profile))

        # タスクトリ
        t0 = Tasktory('', 1)
        t1 = Tasktory('00.あ', 2)
        t2 = Tasktory('01.か', 3)
        t21 = Tasktory('02.き', 4)
        t22 = Tasktory('02.きき', 5)
        t0.append(t1)
        t0.append(t2)
        t2.append(t21)
        t2.append(t22)
        for node in t0:
            Manager.put(self.root, node, self.profile)

        t0_ = Manager.get_tree(self.root, self.profile)
        for n, n_ in zip(t0, t0_):
            self.check(n_, n.name, n.deadline, n_.parent,
                    n.status, n.category, n.comments)
        return

    #==========================================================================
    # get
    #==========================================================================
    def test_get(self):
        # 存在しないパスをgetする
        self.assertFalse(os.path.exists(self.root))
        self.assertIsNone(Manager.get(self.root, self.profile))

        # タスクトリでないディレクトリをgetする
        self.assertIsNone(Manager.get('/Users/taku', self.profile))

        # 空タスクトリをputしてからgetする
        t0 = Tasktory('', 1)
        Manager.put(self.root, t0, self.profile)
        self.assertTrue(os.path.exists(self.root))
        self.assertTrue(os.path.isfile(os.path.join(self.root, self.profile)))
        t0_ = Manager.get(self.root, self.profile, False)
        self.assertIsNot(t0, t0_)
        self.check(t0_, '', 1, None, OPEN, None, '')
        t0_ = Manager.get(self.root, self.profile)
        self.check(t0_, 'work', 1, None, OPEN, None, '')

        # 名前付きタスクトリ
        t1 = Tasktory('#123.あいうえお', 123, CLOSE)
        t1.add_time(10,20)
        t1.comments = 'コメント'
        Manager.put(self.root, t1, self.profile)
        self.assertTrue(os.path.exists(os.path.join(self.root, t1.name)))
        self.assertTrue(os.path.isfile(os.path.join(self.root, t1.name, self.profile)))
        t1_ = Manager.get(os.path.join(self.root, t1.name), self.profile, False)
        self.check(t1_, '#123.あいうえお', 123, None, CLOSE, None, 'コメント')
        return

    #==========================================================================
    # put
    #==========================================================================
    def test_put(self):
        # getと一緒にテストする
        return

    #==========================================================================
    # listtask
    #==========================================================================
    def test_listtask(self):
        # TODO
        return

    #==========================================================================
    # overlap
    #==========================================================================
    def test_overlap(self):
        return

    #==========================================================================
    # same_tree
    #==========================================================================
    def test_same_tree(self):
        # TODO
        return

    #==========================================================================
    # same
    #==========================================================================
    def test_same(self):
        # TODO
        return

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
