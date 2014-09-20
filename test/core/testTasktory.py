#!python3
#!C:/python/python3.4/python
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
        # 基本
        self.t0 = Tasktory(0, '', 1)

        # ID
        self.ti1 = Tasktory(1, '', 1)

        # 名前
        self.tn1 = Tasktory(0, '#123.Hoge', 1)
        self.tn2 = Tasktory(0, 'ほげほげ', 1)

        # 期日
        self.td1 = Tasktory(0, '', 2)
        self.td2 = Tasktory(0, '', 3)

        # ステータス
        self.ts0 = Tasktory(0, '', 1, OPEN)
        self.ts1 = Tasktory(0, '', 1, WAIT)
        self.ts2 = Tasktory(0, '', 1, CLOSE)
        self.ts3 = Tasktory(0, '', 1, CONST)

        # タイムテーブル
        self.tt1 = Tasktory(0, '', 1); self.tt1.timetable += [(0, 1)]
        self.tt2 = Tasktory(0, '', 1); self.tt2.timetable += [(1, 2)]
        self.tt3 = Tasktory(0, '', 1); self.tt3.timetable += [(0, 1),(1,2)]

        # 種別
        self.ta1 = Tasktory(0, '', 1); self.ta1.category = 0
        self.ta2 = Tasktory(0, '', 1); self.ta2.category = 1
        self.ta3 = Tasktory(0, '', 1); self.ta3.category = '種別１'

        # コメント
        self.tc1 = Tasktory(0, '', 1); self.tc1.comments = 'HOGEHOGE\n'
        self.tc2 = Tasktory(0, '', 1); self.tc2.comments = 'FUGAFUGA'

        # 親子
        self.tp1 = Tasktory(0, 'Proj1', 1)
        self.tp11 = Tasktory(1, 'LargeTask1', 2); self.tp11.status = WAIT
        self.tp11.timetable += [(0, 1)]
        self.tp111 = Tasktory(2, 'SmallTask1', 3); self.tp111.status = CLOSE
        self.tp111.timetable += [(1, 2)]
        self.tp1.append(self.tp11)
        self.tp11.append(self.tp111)

        self.tp2 = Tasktory(0, 'Proj2', 1)
        self.tp21 = Tasktory(1, 'LargeTask1', 2); self.tp21.status = WAIT
        self.tp21.timetable += [(0, 1)]
        self.tp22 = Tasktory(2, 'LargeTask2', 3); self.tp22.status = CLOSE
        self.tp2.append(self.tp21)
        self.tp2.append(self.tp22)

        self.tp3 = Tasktory(0, 'Proj3', 1)
        self.tp31 = Tasktory(1, 'LargeTask1', 2); self.tp31.status = OPEN
        self.tp311 = Tasktory(2, 'SmallTask1', 3); self.tp311.status = OPEN
        self.tp312 = Tasktory(3, 'SmallTask2', 4); self.tp312.status = CLOSE
        self.tp312.timetable += [(0, 1), (7, 8)]
        self.tp32 = Tasktory(4, 'LargeTask2', 5); self.tp32.status = CLOSE
        self.tp323 = Tasktory(5, 'SmallTask3', 6); self.tp323.status = WAIT
        self.tp323.timetable += [(1, 2)]
        self.tp324 = Tasktory(6, 'SmallTask4', 7); self.tp324.status = CONST
        self.tp324.timetable += [(3, 4)]
        self.tp3.append(self.tp31)
        self.tp31.append(self.tp311)
        self.tp31.append(self.tp312)
        self.tp3.append(self.tp32)
        self.tp32.append(self.tp323)
        self.tp32.append(self.tp324)

        # ID, 期日
        self.ti1d1 = Tasktory(1, '', 2)

        # 名前, タイムテーブル
        self.tn2t2 = Tasktory(0, 'ほげほげ', 1)
        self.tn2t2.timetable += [(1, 2)]

        # 期日, タイムテーブル
        self.td2t2 = Tasktory(0, '', 3)
        self.td2t2.timetable += [(1, 2)]

        # ステータス, タイムテーブル
        self.ts2t2 = Tasktory(0, '', 1, CLOSE)
        self.ts2t2.timetable += [(1, 2)]

        # タイムテーブル, 種別
        self.tt2a2 = Tasktory(0, '', 1); self.tt2a2.category = 1
        self.tt2a2.timetable += [(1, 2)]

        # タイムテーブル, コメント
        self.tc2t2 = Tasktory(0, '', 1)
        self.tc2t2.comments = 'FUGAFUGA'
        self.tc2t2.timetable += [(1, 2)]

        # ID, 期日, タイムテーブル
        self.ti1d1t1 = Tasktory(1, '', 2); self.ti1d1t1.timetable += [(0,1)]
        self.ti1d1t2 = Tasktory(1, '', 2); self.ti1d1t2.timetable += [(1,2)]
        self.ti1d1t3 = Tasktory(1, '', 2); self.ti1d1t3.timetable += [(0,1),(1,2)]

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

        # ステータス
        self.check(self.ts0, 0, '', 1, None, OPEN, None, '')
        self.check(self.ts1, 0, '', 1, None, WAIT, None, '')
        self.check(self.ts2, 0, '', 1, None, CLOSE, None, '')
        self.check(self.ts3, 0, '', 1, None, CONST, None, '')

        return

    #==========================================================================
    # 比較／テスト
    #==========================================================================
    def test_lt(self):
        # 大小関係がタイムテーブルによって決定する事を確認する
        # ID, 期日は無関係である事も確認する

        # タイムテーブルの値で結果を確認する
        self.assertFalse(self.t0 < self.t0)
        self.assertFalse(self.t0 < self.tt1)
        self.assertTrue(self.tt1 < self.tt2)
        self.assertFalse(self.tt2 < self.tt3)
        self.assertFalse(self.tt2 < self.tt1)

        # ID, 期日が無関係である事を確認する
        self.assertFalse(self.t0 < self.ti1d1)
        self.assertFalse(self.t0 < self.ti1d1t1)
        self.assertTrue(self.tt1 < self.ti1d1t2)
        self.assertFalse(self.tt2 < self.ti1d1t3)
        self.assertFalse(self.tt2 < self.ti1d1t1)
        return

    def test_le(self):
        # タイムテーブルの値で結果を確認する
        self.assertTrue(self.t0 <= self.t0)
        self.assertTrue(self.t0 <= self.tt1)
        self.assertTrue(self.tt1 <= self.tt2)
        self.assertTrue(self.tt2 <= self.tt3)
        self.assertFalse(self.tt2 <= self.tt1)

        # ID, 期日が無関係である事を確認する
        self.assertTrue(self.t0 <= self.ti1d1)
        self.assertTrue(self.t0 <= self.ti1d1t1)
        self.assertTrue(self.tt1 <= self.ti1d1t2)
        self.assertTrue(self.tt2 <= self.ti1d1t3)
        self.assertFalse(self.tt2 <= self.ti1d1t1)
        return

    def test_eq(self):
        # IDで決定する事を確認する
        self.assertTrue(self.t0 == self.t0)
        self.assertFalse(self.t0 == self.ti1)
        self.assertTrue(self.ti1 == self.ti1)

        # ID以外は無関係である事を確認する
        self.assertTrue(self.t0 == self.tn1)
        self.assertTrue(self.t0 == self.td1)
        self.assertTrue(self.t0 == self.ts1)
        self.assertTrue(self.t0 == self.tt1)

        self.assertFalse(self.ti1 == self.tn1)
        self.assertFalse(self.ti1 == self.td1)
        self.assertFalse(self.ti1 == self.ts1)
        self.assertFalse(self.ti1 == self.tt1)
        return

    def test_ne(self):
        # IDで決定する事を確認する
        self.assertFalse(self.t0 != self.t0)
        self.assertTrue(self.t0 != self.ti1)
        self.assertFalse(self.ti1 != self.ti1)

        # ID以外は無関係である事を確認する
        self.assertFalse(self.t0 != self.tn1)
        self.assertFalse(self.t0 != self.td1)
        self.assertFalse(self.t0 != self.ts1)
        self.assertFalse(self.t0 != self.tt1)

        self.assertTrue(self.ti1 != self.tn1)
        self.assertTrue(self.ti1 != self.td1)
        self.assertTrue(self.ti1 != self.ts1)
        self.assertTrue(self.ti1 != self.tt1)
        return

    def test_gt(self):
        # タイムテーブルの値で結果を確認する
        self.assertFalse(self.t0 > self.t0)
        self.assertFalse(self.t0 > self.tt1)
        self.assertFalse(self.tt1 > self.tt2)
        self.assertFalse(self.tt2 > self.tt3)
        self.assertTrue(self.tt2 > self.tt1)

        # ID, 期日が無関係である事を確認する
        self.assertFalse(self.t0 > self.ti1d1)
        self.assertFalse(self.t0 > self.ti1d1t1)
        self.assertFalse(self.tt1 > self.ti1d1t2)
        self.assertFalse(self.tt2 > self.ti1d1t3)
        self.assertTrue(self.tt2 > self.ti1d1t1)
        return

    def test_ge(self):
        # タイムテーブルの値で結果を確認する
        self.assertTrue(self.t0 >= self.t0)
        self.assertTrue(self.t0 >= self.tt1)
        self.assertFalse(self.tt1 >= self.tt2)
        self.assertTrue(self.tt2 >= self.tt3)
        self.assertTrue(self.tt2 >= self.tt1)

        # ID, 期日が無関係である事を確認する
        self.assertTrue(self.t0 >= self.ti1d1)
        self.assertTrue(self.t0 >= self.ti1d1t1)
        self.assertFalse(self.tt1 >= self.ti1d1t2)
        self.assertTrue(self.tt2 >= self.ti1d1t3)
        self.assertTrue(self.tt2 >= self.ti1d1t1)
        return

    def test_bool(self):
        # 内容に関係なくTrueである事を確認する
        self.assertTrue(bool(self.t0))
        self.assertTrue(bool(self.ti1))
        self.assertTrue(bool(self.tn1))
        self.assertTrue(bool(self.td1))
        self.assertTrue(bool(self.ts1))
        self.assertTrue(bool(self.tt1))
        return

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def test_len(self):
        # 子の数によってのみ決定する事を確認する
        self.assertEqual(len(self.t0), 1)
        self.assertEqual(len(self.ti1), 1)
        self.assertEqual(len(self.tn1), 1)
        self.assertEqual(len(self.td1), 1)
        self.assertEqual(len(self.ts1), 1)
        self.assertEqual(len(self.tt1), 1)
        self.assertEqual(len(self.tp1), 3)
        self.assertEqual(len(self.tp11), 2)
        self.assertEqual(len(self.tp111), 1)
        self.assertEqual(len(self.tp2), 3)
        self.assertEqual(len(self.tp21), 1)
        self.assertEqual(len(self.tp22), 1)
        self.assertEqual(len(self.tp3), 7)
        return

    def test_getitem(self):
        self.assertIs(self.t0[0], self.t0)
        self.assertRaises(IndexError, self.t0.__getitem__, 1)

        self.assertIs(self.tp1[0], self.tp1)
        self.assertIs(self.tp1[1], self.tp11)
        self.assertIs(self.tp1[2], self.tp111)

        self.assertIs(self.tp2[0], self.tp2)
        self.assertIs(self.tp2[1], self.tp21)
        self.assertIs(self.tp2[2], self.tp22)

        self.assertIs(self.tp3[0], self.tp3)
        self.assertIs(self.tp3[1], self.tp31)
        self.assertIs(self.tp3[2], self.tp311)
        self.assertIs(self.tp3[3], self.tp312)
        self.assertIs(self.tp3[4], self.tp32)
        self.assertIs(self.tp3[5], self.tp323)
        self.assertIs(self.tp3[6], self.tp324)

        self.assertRaises(IndexError, self.tp31.__getitem__, 0)
        self.assertIs(self.tp31[1], self.tp31)
        self.assertIs(self.tp31[2], self.tp311)
        self.assertIs(self.tp31[3], self.tp312)
        self.assertRaises(IndexError, self.tp31.__getitem__, 4)
        return

    def test_setitem(self):
        # getitemで参照してwashを呼び出しているだけなので、控えめでOK
        self.check(self.t0, 0, '', 1, None, OPEN, None, '')

        self.t0[0] = self.tn1
        self.check(self.t0, 0, '#123.Hoge', 1, None, OPEN, None, '')
        self.check_child(self.t0)
        self.check_time(self.t0)

        self.t0[0] = self.td1
        self.check(self.t0, 0, '', 2, None, OPEN, None, '')
        self.check_child(self.t0)
        self.check_time(self.t0)

        self.tp1[2] = Tasktory(2, 'Number2', 10)
        self.check(self.tp1[2], 2, 'Number2', 10, None, OPEN, None, '')
        return

    def test_iter(self):
        # list化して順番を確認する
        for node in self.t0: self.assertIs(node, self.t0)
        self.assertListEqual(list(self.t0), [self.t0])
        self.assertListEqual(list(self.tp1), [self.tp1, self.tp11, self.tp111])
        self.assertListEqual(list(self.tp2), [self.tp2, self.tp21, self.tp22])
        self.assertListEqual(list(self.tp3), [self.tp3, self.tp31, self.tp311,
            self.tp312, self.tp32, self.tp323, self.tp324])
        return

    def test_contains(self):
        # IDによって決定する事を確認する
        self.assertTrue(self.t0 in self.t0)
        self.assertFalse(self.ti1 in self.t0)
        self.assertTrue(self.tn1 in self.t0)

        # Tasktory型以外ではTypeErrorになる事を確認する
        self.assertRaises(TypeError, self.t0.__contains__, 0)
        self.assertRaises(TypeError, self.t0.__contains__, '')

        # 子持ちに大しても正常に動作するか確認する
        self.assertTrue(self.tp1 in self.tp1)
        self.assertTrue(self.tp11 in self.tp1)
        self.assertTrue(self.tp111 in self.tp1)

        self.assertTrue(self.tp2 in self.tp2)
        self.assertTrue(self.tp21 in self.tp2)
        self.assertTrue(self.tp22 in self.tp2)

        self.assertTrue(self.tp3 in self.tp3)
        self.assertTrue(self.tp31 in self.tp3)
        self.assertTrue(self.tp311 in self.tp3)
        self.assertTrue(self.tp312 in self.tp3)
        self.assertTrue(self.tp32 in self.tp3)
        self.assertTrue(self.tp323 in self.tp3)
        self.assertTrue(self.tp324 in self.tp3)

        self.assertFalse(self.tp3 in self.tp31)
        self.assertTrue(self.tp31 in self.tp31)
        self.assertTrue(self.tp311 in self.tp31)
        self.assertTrue(self.tp312 in self.tp31)
        self.assertFalse(self.tp32 in self.tp31)
        self.assertFalse(self.tp323 in self.tp31)
        self.assertFalse(self.tp324 in self.tp31)
        return

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def test_add(self):
        # 名前は新しい方を使用し、順番は関係ない事を確認する
        self.check(self.t0 + self.tn1, 0, '#123.Hoge', 1, None, OPEN, None, '')
        self.check(self.tn1 + self.t0, 0, '', 1, None, OPEN, None, '')
        self.check(self.tn1 + self.tn2t2, 0, 'ほげほげ', 1, None, OPEN, None, '')
        self.check(self.tn2t2 + self.tn1, 0, 'ほげほげ', 1, None, OPEN, None, '')
        self.check(self.tt2 + self.tn1, 0, '', 1, None, OPEN, None, '')
        self.check(self.tn1 + self.tt2, 0, '', 1, None, OPEN, None, '')

        # 期日は新しい方を使用し、順番は関係ない事を確認する
        self.check(self.t0 + self.td1, 0, '', 2, None, OPEN, None, '')
        self.check(self.td1 + self.t0, 0, '', 1, None, OPEN, None, '')
        self.check(self.td1 + self.td2t2, 0, '', 3, None, OPEN, None, '')
        self.check(self.td2t2 + self.td1, 0, '', 3, None, OPEN, None, '')

        # ステータスは新しい方を使用し、順番は関係ない事を確認する
        self.check(self.t0 + self.ts1, 0, '', 1, None, WAIT, None, '')
        self.check(self.ts1 + self.t0, 0, '', 1, None, OPEN, None, '')
        self.check(self.ts1 + self.ts2t2, 0, '', 1, None, CLOSE, None, '')
        self.check(self.ts2t2 + self.ts1, 0, '', 1, None, CLOSE, None, '')

        # タイムテーブルは単純結合される事を確認する
        self.check_time(self.t0 + self.tn1)
        self.check_time(self.t0 + self.tt1, (0,1))
        self.check_time(self.tt1 + self.t0, (0,1))
        self.check_time(self.tt1 + self.tt2, (0,1), (1,2))
        self.check_time(self.tt2 + self.tt1, (1,2), (0,1))
        self.check_time(self.tt1 + self.tt3, (0,1), (0,1), (1,2))

        # 親子
        t1 = Tasktory(0, 'PROJ1', 1)
        self.assertListEqual([n.name for n in self.tp1 + t1],
                ['PROJ1', 'LargeTask1', 'SmallTask1'])
        self.assertListEqual([n.name for n in t1 + self.tp1],
                ['Proj1', 'LargeTask1', 'SmallTask1'])

        t1 = Tasktory(0, 'PROJ1', 1)
        t11 = Tasktory(1, 'LARGETASK1', 2)
        t111 = Tasktory(2, 'SMALLTASK1', 3)
        t1.append(t11)
        t11.append(t111)
        self.assertListEqual([n.name for n in self.tp1 + t1],
                ['PROJ1', 'LARGETASK1', 'SmallTask1'])
        self.assertListEqual([n.name for n in t1 + self.tp1],
                ['Proj1', 'LargeTask1', 'SmallTask1'])

        t1 = Tasktory(0, 'PROJ1', 1); t1.timetable += [(2,10)]
        t11 = Tasktory(1, 'LARGETASK1', 2); t11.timetable += [(2,10)]
        t111 = Tasktory(2, 'SMALLTASK1', 3); t111.timetable += [(2,10)]
        t1.append(t11)
        t11.append(t111)
        self.assertListEqual([n.name for n in self.tp1 + t1],
                ['PROJ1', 'LARGETASK1', 'SMALLTASK1'])
        self.assertListEqual([n.name for n in t1 + self.tp1],
                ['PROJ1', 'LARGETASK1', 'SMALLTASK1'])

        t3 = Tasktory(0, 'PROJ3', 1); t3.timetable += [(2,10)]
        t31 = Tasktory(1, 'LARGETASK1', 1)
        t311 = Tasktory(2, 'SMALLTASK1', 1); t311.timetable += [(2,10)]
        t312 = Tasktory(3, 'SMALLTASK2', 1); t312.timetable += [(2,10)]
        t32 = Tasktory(4, 'LARGETASK2', 1); t32.timetable += [(2,10)]
        t323 = Tasktory(5, 'SMALLTASK3', 1)
        t324 = Tasktory(6, 'SMALLTASK4', 1)
        t3.append(t31)
        t31.append(t311)
        t31.append(t312)
        t3.append(t32)
        t32.append(t323)
        t32.append(t324)
        self.assertListEqual([n.name for n in self.tp3 + t3],
                ['PROJ3', 'LARGETASK1', 'SMALLTASK1', 'SmallTask2',
                    'LARGETASK2', 'SmallTask3', 'SmallTask4'])
        self.assertListEqual([n.name for n in t3 + self.tp3],
                ['PROJ3', 'LargeTask1', 'SMALLTASK1', 'SmallTask2',
                    'LARGETASK2', 'SmallTask3', 'SmallTask4'])

        # 種別は新しい方が優先される事を確認する
        self.check(self.t0 + self.ta1, 0, '', 1, None, OPEN, 0, '')
        self.check(self.t0 + self.ta2, 0, '', 1, None, OPEN, 1, '')
        self.check(self.t0 + self.ta3, 0, '', 1, None, OPEN, '種別１', '')
        self.check(self.ta1 + self.ta2, 0, '', 1, None, OPEN, 1, '')
        self.check(self.ta2 + self.ta1, 0, '', 1, None, OPEN, 0, '')
        self.check(self.ta2 + self.tt2, 0, '', 1, None, OPEN, 1, '')
        self.check(self.tt2 + self.ta2, 0, '', 1, None, OPEN, 1, '')
        self.check(self.ta3 + self.tt2a2, 0, '', 1, None, OPEN, 1, '')
        self.check(self.tt2a2 + self.ta3, 0, '', 1, None, OPEN, 1, '')

        # コメントは新しい方を使用し、順番は関係ない事を確認する
        self.check(self.t0 + self.tc1, 0, '', 1, None, OPEN, None, 'HOGEHOGE\n')
        self.check(self.tc1 + self.t0, 0, '', 1, None, OPEN, None, '')
        self.check(self.tc1 + self.tc2t2, 0, '', 1, None, OPEN, None, 'FUGAFUGA')
        self.check(self.tc2t2 + self.tc1, 0, '', 1, None, OPEN, None, 'FUGAFUGA')

        # IDが一致しなければValueErrorになる事を確認する
        self.assertRaises(ValueError, self.t0.__add__, self.ti1)
        return

    #==========================================================================
    # タスクトリデータ参照メソッド
    #==========================================================================
    def test_timetable_of_tree(self):
        # 子無し
        self.assertSequenceEqual(self.t0.timetable_of_tree(), [])
        self.assertSequenceEqual(self.tt1.timetable_of_tree(), [(0,1)])
        self.assertSequenceEqual(self.tt3.timetable_of_tree(), [(0,1), (1,2)])

        # 子持ち
        self.assertSequenceEqual(self.tp1.timetable_of_tree(), [(0,1), (1,2)])
        self.assertSequenceEqual(self.tp11.timetable_of_tree(), [(0,1), (1,2)])
        self.assertSequenceEqual(self.tp111.timetable_of_tree(), [(1,2)])

        self.assertSequenceEqual(self.tp2.timetable_of_tree(), [(0,1)])
        self.assertSequenceEqual(self.tp21.timetable_of_tree(), [(0,1)])
        self.assertSequenceEqual(self.tp22.timetable_of_tree(), [])

        self.assertSequenceEqual(self.tp3.timetable_of_tree(),
                [(0,1),(7,8),(1,2),(3,4)])
        self.assertSequenceEqual(self.tp31.timetable_of_tree(), [(0,1),(7,8)])
        self.assertSequenceEqual(self.tp32.timetable_of_tree(), [(1,2),(3,4)])
        return

    def test_total_time(self):
        # 子無し
        self.assertEqual(self.t0.total_time(), 0)
        self.assertEqual(self.tt1.total_time(), 1)
        self.assertEqual(self.tt2.total_time(), 2)
        self.assertEqual(self.tt3.total_time(), 3)

        # 子持ち
        self.assertEqual(self.tp1.total_time(), 0)
        self.assertEqual(self.tp11.total_time(), 1)
        self.assertEqual(self.tp111.total_time(), 2)
        return

    def test_total_time_of_tree(self):
        # 子無し
        self.assertEqual(self.t0.total_time_of_tree(), 0)
        self.assertEqual(self.tt1.total_time_of_tree(), 1)
        self.assertEqual(self.tt2.total_time_of_tree(), 2)
        self.assertEqual(self.tt3.total_time_of_tree(), 3)

        # 子持ち
        self.assertEqual(self.tp1.total_time_of_tree(), 3)
        self.assertEqual(self.tp11.total_time_of_tree(), 3)
        self.assertEqual(self.tp111.total_time_of_tree(), 2)

        self.assertEqual(self.tp2.total_time_of_tree(), 1)
        self.assertEqual(self.tp21.total_time_of_tree(), 1)
        self.assertEqual(self.tp22.total_time_of_tree(), 0)

        self.assertEqual(self.tp3.total_time_of_tree(), 15)
        self.assertEqual(self.tp31.total_time_of_tree(), 9)
        self.assertEqual(self.tp32.total_time_of_tree(), 6)
        return

    def test_timestamp(self):
        # タイムテーブルで決定する事を確認する
        self.assertEqual(self.t0.timestamp(), 0)
        self.assertEqual(self.tt1.timestamp(), 0)
        self.assertEqual(self.tt2.timestamp(), 1)
        self.assertEqual(self.tt3.timestamp(), 1)

        # ID, 期日に関係ない事を確認する
        self.assertEqual(self.ti1d1.timestamp(), 0)
        self.assertEqual(self.ti1d1t1.timestamp(), 0)
        self.assertEqual(self.ti1d1t2.timestamp(), 1)
        self.assertEqual(self.ti1d1t3.timestamp(), 1)
        return

    #==========================================================================
    # タスクトリデータ変更メソッド
    #==========================================================================
    def test_add_time(self):
        self.check_time(self.t0)
        self.t0.add_time(0, 1)
        self.check_time(self.t0, (0,1))
        self.t0.add_time(1, 2)
        self.check_time(self.t0, (0,1), (1,2))
        self.t0.add_time(1, 2)
        self.check_time(self.t0, (0,1), (1,2), (1,2))
        return

    def test_append(self):
        self.check_child(self.t0)
        self.check(self.ti1, 1, '', 1, None, OPEN, None, '')
        self.check(self.tn1, 0, '#123.Hoge', 1, None, OPEN, None, '')

        self.t0.append(self.ti1)
        self.check_child(self.t0, self.ti1)
        self.check(self.ti1, 1, '', 1, self.t0, OPEN, None, '')

        self.t0.append(self.tn1)
        self.check_child(self.t0, self.ti1, self.tn1)
        self.check(self.tn1, 0, '#123.Hoge', 1, self.t0, OPEN, None, '')
        return

    #==========================================================================
    # 抽象データ参照メソッド
    #==========================================================================
    def test_get(self):
        self.assertIs(self.t0.get(0), self.t0)
        self.assertIsNone(self.t0.get(1))
        self.assertFalse(self.t0.get(1, False))

        self.assertIs(self.tp1.get(0), self.tp1)
        self.assertIs(self.tp1.get(1), self.tp11)
        self.assertIs(self.tp1.get(2), self.tp111)

        self.assertIs(self.tp2.get(0), self.tp2)
        self.assertIs(self.tp2.get(1), self.tp21)
        self.assertIs(self.tp2.get(2), self.tp22)

        self.assertIs(self.tp3.get(0), self.tp3)
        self.assertIs(self.tp3.get(1), self.tp31)
        self.assertIs(self.tp3.get(2), self.tp311)
        self.assertIs(self.tp3.get(3), self.tp312)
        self.assertIs(self.tp3.get(4), self.tp32)
        self.assertIs(self.tp3.get(5), self.tp323)
        self.assertIs(self.tp3.get(6), self.tp324)

        self.assertIs(self.tp31.get(0), None)
        self.assertIs(self.tp31.get(1), self.tp31)
        self.assertIs(self.tp31.get(2), self.tp311)
        self.assertIs(self.tp31.get(3), self.tp312)
        self.assertIs(self.tp31.get(4), None)
        return

    def test_path(self):
        # 子無し
        self.assertEqual(self.t0.path(), '/')
        self.assertEqual(self.t0.path('/hoge'), '/hoge/')
        self.assertEqual(self.tn1.path(), '/#123.Hoge')
        self.assertEqual(self.tn1.path('/hoge'), '/hoge/#123.Hoge')
        nf = lambda t:'{}.{}'.format(t.ID, t.name)
        self.assertEqual(self.tn1.path(namefunc=nf), '/0.#123.Hoge')
        self.assertEqual(self.tn1.path('/hoge', namefunc=nf),
                '/hoge/0.#123.Hoge')

        # 子持ち
        self.assertEqual(self.tp1.path(), '/Proj1')
        self.assertEqual(self.tp11.path(), '/Proj1/LargeTask1')
        self.assertEqual(self.tp111.path(), '/Proj1/LargeTask1/SmallTask1')
        self.assertEqual(self.tp111.path('/hoge'),
                '/hoge/Proj1/LargeTask1/SmallTask1')
        self.assertEqual(self.tp111.path(namefunc=nf),
                '/0.Proj1/1.LargeTask1/2.SmallTask1')
        self.assertEqual(self.tp111.path('/hoge', namefunc=nf),
                '/hoge/0.Proj1/1.LargeTask1/2.SmallTask1')
        return

    def test_level(self):
        # 子無し
        self.assertEqual(self.t0.level(), 0)
        self.assertEqual(self.ti1.level(), 0)
        self.assertEqual(self.tn1.level(), 0)
        self.assertEqual(self.td1.level(), 0)
        self.assertEqual(self.ts1.level(), 0)

        # 子持ち
        self.assertEqual(self.tp1.level(), 0)
        self.assertEqual(self.tp11.level(), 1)
        self.assertEqual(self.tp111.level(), 2)
        return

    def test_copy(self):
        # 子無し
        self.check(self.t0.copy(), 0, '', 1, None, OPEN, None, '')
        self.check(self.ti1.copy(), 1, '', 1, None, OPEN, None, '')
        self.check(self.tn1.copy(), 0, '#123.Hoge', 1, None, OPEN, None, '')
        self.check(self.td1.copy(), 0, '', 2, None, OPEN, None, '')
        self.check(self.ts1.copy(), 0, '', 1, None, WAIT, None, '')
        self.check(self.tc1.copy(), 0, '', 1, None, OPEN, None, 'HOGEHOGE\n')

        # 子持ち
        self.check(self.tp1.copy(), 0, 'Proj1', 1, None, OPEN, None, '')
        self.check_child(self.tp1.copy())
        self.check(self.tp11.copy(), 1, 'LargeTask1', 2, None, WAIT, None, '')
        self.check_time(self.tp11.copy(), (0,1))
        self.check_child(self.tp11.copy())
        self.check(self.tp111.copy(), 2, 'SmallTask1', 3, None, CLOSE, None, '')
        self.check_time(self.tp111.copy(), (1,2))
        self.check_child(self.tp111.copy())
        return

    def test_copy_of_tree(self):
        # 子無し
        self.check(self.t0.copy_of_tree(), 0, '', 1, None, OPEN, None, '')
        self.check(self.ti1.copy_of_tree(), 1, '', 1, None, OPEN, None, '')
        self.check(self.tn1.copy_of_tree(),
                0, '#123.Hoge', 1, None, OPEN, None, '')
        self.check(self.td1.copy_of_tree(), 0, '', 2, None, OPEN, None, '')
        self.check(self.ts1.copy_of_tree(), 0, '', 1, None, WAIT, None, '')
        self.check(self.tc1.copy_of_tree(),
                0, '', 1, None, OPEN, None, 'HOGEHOGE\n')

        # 子持ち
        self.check(self.tp1.copy_of_tree(),
                0, 'Proj1', 1, None, OPEN, None, '')
        self.check_child(self.tp1.copy_of_tree(), self.tp11)
        self.check(self.tp11.copy_of_tree(),
                1, 'LargeTask1', 2, self.tp1, WAIT, None, '')
        self.check_time(self.tp11.copy_of_tree(), (0,1))
        self.check_child(self.tp11.copy_of_tree(), self.tp111)
        self.check(self.tp111.copy_of_tree(),
                2, 'SmallTask1', 3, self.tp11, CLOSE, None, '')
        self.check_time(self.tp111.copy_of_tree(), (1,2))
        self.check_child(self.tp111.copy_of_tree())

        self.check(self.tp2.copy_of_tree(),
                0, 'Proj2', 1, None, OPEN, None, '')
        self.check_child(self.tp2.copy_of_tree(), self.tp21, self.tp22)
        self.check_time(self.tp2.copy_of_tree())
        self.check(self.tp21.copy_of_tree(),
                1, 'LargeTask1', 2, self.tp2, WAIT, None, '')
        self.check_child(self.tp21.copy_of_tree())
        self.check_time(self.tp21.copy_of_tree(), (0,1))
        self.check(self.tp22.copy_of_tree(),
                2, 'LargeTask2', 3, self.tp2, CLOSE, None, '')
        self.check_child(self.tp22.copy_of_tree())
        self.check_time(self.tp22.copy_of_tree())
        return

    def test_clip(self):
        # 子無し
        self.check(self.t0.clip(), 0, '', 1, None, OPEN, None, '')
        self.assertIsNone(self.t0.clip(lambda t:t.status == CLOSE))

        # 子持ち１（返り値を変更しても元のデータには影響が無い事も確認する）
        t = self.tp1.clip()
        self.check(t, 0, 'Proj1', 1, None, OPEN, None, '')
        self.assertListEqual(list(t), [self.tp1, self.tp11])
        t.status == CLOSE
        t[1].status = CLOSE
        self.assertEqual(self.tp1.status, OPEN)
        self.assertEqual(self.tp11.status, WAIT)

        # 子持ち２
        self.check(self.tp2.clip(), 0, 'Proj2', 1, None, OPEN, None, '')
        self.assertListEqual(list(self.tp2.clip()), [self.tp2, self.tp21])

        # 子持ち３
        self.check(self.tp3.clip(), 0, 'Proj3', 1, None, OPEN, None, '')
        self.assertListEqual(list(self.tp3.clip()),
                [self.tp3, self.tp31, self.tp311, self.tp32,
                    self.tp323, self.tp324])
        return

    #==========================================================================
    # 抽象データ変更メソッド
    #==========================================================================
    def test_commit(self):
        # getitem, setitem, add, washを使用しているだけなので、軽めでOK
        self.check(self.t0, 0, '', 1, None, OPEN, None, '')
        self.assertTrue(self.t0.commit(self.tn1))
        self.check(self.t0, 0, '#123.Hoge', 1, None, OPEN, None, '')
        self.assertFalse(self.t0.commit(self.ti1))

        # ツリー内のタスク、小タスクは影響が無い事を確認する
        t = Tasktory(1, 'LARGETASK1', 20, CONST)
        t.add_time(10, 20)
        t.append(Tasktory(2, 'SMALLTASK1', 30, WAIT))
        t[2].add_time(20, 30)
        self.assertTrue(self.tp1.commit(t))
        self.check(self.tp1, 0, 'Proj1', 1, None, OPEN, None, '')
        self.check_time(self.tp1)
        self.check_child(self.tp1, self.tp11)
        self.check(self.tp11, 1, 'LARGETASK1', 20, self.tp1, CONST, None, '')
        self.check_time(self.tp11, (0, 1), (10, 20))
        self.check_child(self.tp11, self.tp111)
        self.check(self.tp111, 2, 'SmallTask1', 3, self.tp11, CLOSE, None, '')
        self.check_time(self.tp111, (1, 2))
        self.check_child(self.tp111)
        return

    def test_wash(self):
        self.check(self.t0, 0, '', 1, None, OPEN, None, '')
        self.assertRaises(ValueError, self.t0.wash, self.ti1)
        self.t0.wash(self.tn1)
        self.check(self.t0, 0, '#123.Hoge', 1, None, OPEN, None, '')
        self.t0.wash(self.td1)
        self.check(self.t0, 0, '', 2, None, OPEN, None, '')
        self.t0.wash(self.ts1)
        self.check(self.t0, 0, '', 1, None, WAIT, None, '')
        self.t0.wash(self.tc1)
        self.check(self.t0, 0, '', 1, None, OPEN, None, 'HOGEHOGE\n')
        self.t0.wash(self.tp1)
        self.check(self.t0, 0, 'Proj1', 1, None, OPEN, None, '')
        self.assertListEqual(list(self.t0), [self.tp1, self.tp11, self.tp111])
        self.ti1.wash(self.tp11)
        self.check(self.ti1, 1, 'LargeTask1', 2, self.tp1, WAIT, None, '')
        self.assertListEqual(list(self.ti1), [self.tp11, self.tp111])
        return

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
