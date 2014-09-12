#!C:/python/python3.4/python
#!python3
#-*- encoding:utf-8 -*-

import sys, os, datetime, unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory

OPEN = Tasktory.OPEN
WAIT = Tasktory.WAIT
CLOSE = Tasktory.CLOSE
CONST = Tasktory.CONST

class TestTasktory(unittest.TestCase):

    def check(self, task, ID, name, deadline, parent,
            status, category, comments):
        self.assertEqual(task.ID, ID)
        self.assertEqual(task.name, name)
        self.assertEqual(task.deadline, deadline)
        self.assertIs(task.parent, parent)
        self.assertEqual(task.status, status)
        self.assertEqual(task.category, category)
        self.assertIs(task.comments, comments)
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
        # ID : 0, 1

        # name : '', '#123.Hoge', 'ほげ'

        # deadline : 1, 2

        # timetable : [], [(0,1)], [(1,2)], [(0,1),(1,2)]

        # parent : None, t
        # children : [], [t], [t, t], [t[t]], [t[t, t], t[t, t]]

        # status : OPEN, WAIT, CLOSE, CONST
        # category : None, '', 'Fuga', 'ふが'
        # comments : '', 'HOGEHOGE', 'あいうえお', 'hoge\n\rあ'

        # 基本
        self.t0 = Tasktory(0, '', 1)

        # ID
        self.ti1 = Tasktory(1, '', 1)

        # 名前
        self.tn1 = Tasktory(0, '#123.Hoge', 1)
        self.tn2 = Tasktory(0, 'ほげほげ', 1)

        # 期日
        self.td1 = Tasktory(0, '', 2)

        return

    def tearDown(self):
        # self\.t.*[0-9] を削除する
        names = [n for n in dir(self)
                if n[0] == 't' and n[-1] in '1234567890' and '_' not in n]
        cmds = ["del self.{}".format(n) for n in names]
        for cmd in cmds: exec(cmd)
        return

    #==========================================================================
    # コンストラクタ
    #==========================================================================
    def test_init(self):
        # 各変数が適切に設定されるかどうかを確認する
        # 各変数の組み合わせは実施しない
        # コンストラクタの引数に指定しないものは１回だけで良い

        # 基本
        self.check(self.t0, 0, '', 1, None, OPEN, None, '')
        self.check_child(self.t0)
        self.check_time(self.t0)

        # ID
        self.check(self.ti1, 1, '', 1, None, OPEN, None, '')

        # 名前
        self.check(self.tn1, 0, '#123.Hoge', 1, None, OPEN, None, '')
        self.check(self.tn2, 0, 'ほげほげ', 1, None, OPEN, None, '')

        # 期日
        self.check(self.td1, 0, '', 2, None, OPEN, None, '')
        return

    #==========================================================================
    # 比較／テスト
    #==========================================================================
    def test_lt(self):
        # TODO
        # 大小関係がタイムテーブルによって決定する事を確認する
        # ID, 期日は無関係である事も確認する
        self.tt1 = Tasktory(0, '', 1); self.tt1.timetable += [(0, 1)]
        self.tt2 = Tasktory(0, '', 1); self.tt2.timetable += [(1, 2)]
        self.tt3 = Tasktory(0, '', 1); self.tt3.timetable += [(0, 1),(1,2)]
        self.ti1d1 = Tasktory(1, '', 2)
        self.ti1d1t1 = Tasktory(1, '', 2); self.ti1d1t1.timetable += [(0, 1)]
        self.ti1d1t2 = Tasktory(1, '', 2); self.ti1d1t1.timetable += [(1, 2)]
        self.ti1d1t3 = Tasktory(1, '', 2); self.ti1d1t1.timetable += [(0, 1),(1,2)]
        self.assertFalse(self.t0 < self.t0)
        #self.assertTrue()
        return

    def test_le(self):
        # TODO
        return

    def test_eq(self):
        # TODO
        return

    def test_ne(self):
        # TODO
        return

    def test_gt(self):
        # TODO
        return

    def test_ge(self):
        # TODO
        return

    def test_bool(self):
        return

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def test_len(self):
        # TODO
        return

    def test_getitem(self):
        # TODO
        return

    def test_setitem(self):
        # TODO
        return

    def test_iter(self):
        # TODO
        return

    def test_contains(self):
        # TODO
        return

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def test_add(self):
        # TODO
        return

    #==========================================================================
    # タスクトリデータ参照メソッド
    #==========================================================================
    def test_timetable_of_tree(self):
        # TODO
        return

    def test_total_time(self):
        # TODO
        return

    def test_total_time_of_tree(self):
        # TODO
        return

    def test_first_timestamp(self):
        # TODO
        return

    def test_last_timestamp(self):
        # TODO
        return

    #==========================================================================
    # タスクトリデータ変更メソッド
    #==========================================================================
    def test_add_time(self):
        # TODO
        return

    def test_append(self):
        # TODO
        return

    #==========================================================================
    # 抽象データ参照メソッド
    #==========================================================================
    def test_get(self):
        # TODO
        return

    def test_path(self):
        # TODO
        return

    def test_level(self):
        # TODO
        return

    def test_copy(self):
        # TODO
        return

    def test_copy_of_tree(self):
        # TODO
        return

    def test_clip(self):
        # TODO
        return

    #==========================================================================
    # 抽象データ変更メソッド
    #==========================================================================
    def test_commit(self):
        # TODO
        return

    def test_jack(self):
        # TODO
        return

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
