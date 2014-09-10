#!python3
#-*- encoding:utf-8 -*-

import sys, os, datetime, unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory

class TestTasktory(unittest.TestCase):

    def check(self, task, name, deadline, status, parent,
            total_time, child_num):
        self.assertEqual(task.name, name)
        self.assertEqual(task.timestamp, timestamp)
        self.assertEqual(task.deadline, deadline)
        self.assertEqual(task.status, status)
        self.assertTrue(task.parent is parent)
        self.assertEqual(len(task.children), childnum)

    def check_child(self, task, *children):
        self.assertListEqual(
                sorted(task.children, key=lambda t:t.ID),
                sorted(children, key=lambda t:t.ID)
                )

    #==========================================================================
    # コンストラクタ
    #==========================================================================
    def test_init(self):
        pass

    #==========================================================================
    # 文字列表現
    #==========================================================================
    def test_repr(self):
        pass

    def test_str(self):
        pass

    #==========================================================================
    # 比較／テスト
    #==========================================================================
    def test_lt(self):
        pass

    def test_le(self):
        pass

    def test_eq(self):
        pass

    def test_ne(self):
        pass

    def test_gt(self):
        pass

    def test_ge(self):
        pass

    def test_bool(self):
        pass

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def test_len(self):
        pass

    def test_getitem(self):
        pass

    def test_setitem(self):
        pass

    def test_iter(self):
        pass

    def test_contains(self):
        pass

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def test_add(self):
        pass

    #==========================================================================
    # タスクトリデータ参照メソッド
    #==========================================================================
    def test_timetable_of_tree(self):
        pass

    def test_total_time(self):
        pass

    def test_total_time_of_tree(self):
        pass

    def test_first_timestamp(self):
        pass

    def test_last_timestamp(self):
        pass

    #==========================================================================
    # タスクトリデータ変更メソッド
    #==========================================================================
    def test_add_time(self):
        pass

    def test_append(self):
        pass

    #==========================================================================
    # タスクトリデータ参照メソッド
    #==========================================================================
    def test_get(self):
        pass

    def test_path(self):
        pass

    def test_level(self):
        pass

    def test_copy(self):
        pass

    #==========================================================================
    # タスクトリデータ変更メソッド
    #==========================================================================
    def test_commit(self):
        pass

    def test_jack(self):
        pass

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
