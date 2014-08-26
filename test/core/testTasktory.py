#!/usr/bin/env python3
#-*- encoding:utf-8 -*-

import sys, os
import datetime
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
append_path = lambda p:sys.path.append(CURRENT_DIR + '/' + p)
append_path('../../lib/core')

from Tasktory import Tasktory

class TestTasktory(unittest.TestCase):

    def check(self, task, name, timestamp, deadline, start, end, time,
            parent, childnum, status):
        self.assertEqual(task.name, name)
        self.assertEqual(task.timestamp, timestamp)
        self.assertEqual(task.deadline, deadline)
        self.assertEqual(task.start, start)
        self.assertEqual(task.end, end)
        self.assertEqual(task.get_time(), time)
        #self.assertEqual(task.time, time)
        #self.assertEqual(task.parent, parent)
        self.assertTrue(task.parent is parent)
        self.assertEqual(len(task.children), childnum)
        self.assertEqual(task.status, status)

    #==========================================================================
    # コンストラクタ
    #==========================================================================
    def test_init(self):
        t = Tasktory(1, '', 0)
        self.check(t, '', 0, None, None, None, 0, None, 0, Tasktory.OPEN)

        t = Tasktory(1, 'task0', 1)
        self.check(t, 'task0', 1, None, None, None, 0, None, 0, Tasktory.OPEN)

        t = Tasktory(1, 'タスク', 1)
        self.check(t, 'タスク', 1, None, None, None, 0, None, 0, Tasktory.OPEN)

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
        t0 = Tasktory(1, '', 0)
        t1 = Tasktory(1, '', 0)
        t2 = Tasktory(1, 'hoge', 1)
        t3 = Tasktory(2, '', 0)
        t4 = Tasktory(3, 'hoge', 0)
        t5 = Tasktory(4, '1234', 0)
        t6 = Tasktory(5, 'タスク', 0)

        self.assertEqual(t0 == None, False)
        self.assertEqual(t0 == 1, True)
        self.assertEqual(t0 == 2, False)
        self.assertEqual(t0 == '', True)
        self.assertEqual(t0 == 'hoge', False)
        self.assertEqual(t0 == t1, True)
        self.assertEqual(t0 == t2, True)
        self.assertEqual(t0 == t3, False)

        self.assertEqual(t2 == None, False)
        self.assertEqual(t2 == 1, True)
        self.assertEqual(t2 == 2, False)
        self.assertEqual(t2 == '', False)
        self.assertEqual(t2 == 'hoge', True)
        self.assertEqual(t2 == t0, True)
        self.assertEqual(t2 == t4, False)

        self.assertEqual(t5 == '1234', True)
        self.assertEqual(t6 == 'タスク', True)

    def test_ne(self):
        t0 = Tasktory(1, '', 0)
        t1 = Tasktory(1, '', 0)
        t2 = Tasktory(1, 'hoge', 1)
        t3 = Tasktory(2, '', 0)
        t4 = Tasktory(3, 'hoge', 0)
        t5 = Tasktory(4, '1234', 0)
        t6 = Tasktory(5, 'タスク', 0)

        self.assertEqual(t0 != None, True)
        self.assertEqual(t0 != 1, False)
        self.assertEqual(t0 != 2, True)
        self.assertEqual(t0 != '', False)
        self.assertEqual(t0 != 'hoge', True)
        self.assertEqual(t0 != t1, False)
        self.assertEqual(t0 != t2, False)
        self.assertEqual(t0 != t3, True)

        self.assertEqual(t2 != None, True)
        self.assertEqual(t2 != 1, False)
        self.assertEqual(t2 != 2, True)
        self.assertEqual(t2 != '', True)
        self.assertEqual(t2 != 'hoge', False)
        self.assertEqual(t2 != t0, False)
        self.assertEqual(t2 != t4, True)

        self.assertEqual(t5 != '1234', False)
        self.assertEqual(t6 != 'タスク', False)

    def test_gt(self):
        pass

    def test_ge(self):
        pass

    def test_bool(self):
        t1 = Tasktory(1, '', 0)
        t2 = Tasktory(2, 'hoge', 1)
        t3 = Tasktory(3, 'タスク', 2)

        self.assertEqual(bool(t1), True)
        self.assertEqual(bool(t2), True)
        self.assertEqual(bool(t3), True)

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def test_len(self):
        t = Tasktory(1, '', 0)
        self.assertEqual(len(t), 0)

        t.children.append(Tasktory(2, 'c0', 0))
        self.assertEqual(len(t), 1)

        t.children.append(Tasktory(3, 'c1', 1))
        self.assertEqual(len(t), 2)

        t.children.append(1)
        self.assertEqual(len(t), 3)

        t.children.append('hoge')
        self.assertEqual(len(t), 4)

    def test_getitem(self):
        task0 = Tasktory(1, 'task0', 1)
        task1 = Tasktory(2, 'task1', 2)
        task2 = Tasktory(3, 'task2', 3)
        task3 = Tasktory(4, 'task3', 4)
        task0.append(task1)
        task0.append(task2)
        task0.append(task3)
        self.check(task0[0],
                'task1', 2, None, None, None, 0, task0, 0, Tasktory.OPEN)
        self.check(task0[1],
                'task2', 3, None, None, None, 0, task0, 0, Tasktory.OPEN)
        self.check(task0[2],
                'task3', 4, None, None, None, 0, task0, 0, Tasktory.OPEN)

        self.check(task0[1:2][0],
                'task2', 3, None, None, None, 0, task0, 0, Tasktory.OPEN)

        self.check(task0['task1'],
                'task1', 2, None, None, None, 0, task0, 0, Tasktory.OPEN)
        self.check(task0['task2'],
                'task2', 3, None, None, None, 0, task0, 0, Tasktory.OPEN)
        self.check(task0['task3'],
                'task3', 4, None, None, None, 0, task0, 0, Tasktory.OPEN)
        pass

    def test_iter(self):
        task0 = Tasktory(1, 'task0', 1)
        task1 = Tasktory(2, 'task1', 2)
        task2 = Tasktory(3, 'task2', 3)
        task3 = Tasktory(5, 'task3', 5)
        task0.append(task1)
        task0.append(task2)
        task1.append(task3)
        for i,t in enumerate(task0):
            self.assertEqual(t.ID, i+2)
            self.assertEqual(t.name, 'task{0}'.format(i+1))
            self.assertEqual(t.timestamp, i+2)

    def test_contains(self):
        task0 = Tasktory(10, 'task0', 1)
        task1 = Tasktory(20, 'task1', 2)
        task2 = Tasktory(30, 'task2', 3)
        task3 = Tasktory(40, 'task3', 4)
        task0.append(task1)
        task0.append(task2)
        task1.append(task3)
        self.assertEqual(20 in task0, True)
        self.assertEqual('task1' in task0, True)
        self.assertEqual(task1 in task0, True)
        self.assertEqual(30 in task0, True)
        self.assertEqual('task2' in task0, True)
        self.assertEqual(task2 in task0, True)
        self.assertEqual(40 in task0, False)
        self.assertEqual('task3' in task0, False)
        self.assertEqual(task3 in task0, False)

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def test_add(self):
        # タスク名／タイムスタンプ
        t1 = Tasktory('hoge', 1)
        t2 = Tasktory('hoge', 2)
        self.check(t1+t1,'hoge',1,None,None,None,0,None,0,Tasktory.OPEN)
        self.check(t1+t2,'hoge',2,None,None,None,0,None,0,Tasktory.OPEN)
        self.check(t2+t1,'hoge',2,None,None,None,0,None,0,Tasktory.OPEN)
        self.check(t2+t2,'hoge',2,None,None,None,0,None,0,Tasktory.OPEN)

        # 期日／開始日／終了日／作業時間／ステータス
        t10 = Tasktory('hoge', 1)
        t11 = Tasktory('hoge', 1); t11.deadline = 10; t11.start = 100
        t11.end = 101; t11.timetable = [(1, 120)]; t11.status = Tasktory.WAIT
        t12 = Tasktory('hoge', 1); t12.deadline = 20; t12.start = 200
        t12.end = 202; t12.timetable = [(1, 210)]; t12.status = Tasktory.CLOSE
        t20 = Tasktory('hoge', 2)
        t21 = Tasktory('hoge', 2); t21.deadline = 10; t21.start = 100
        t21.end = 101; t21.timetable = [(1, 120)]; t21.status = Tasktory.WAIT
        t22 = Tasktory('hoge', 2); t22.deadline = 20; t22.start = 200
        t22.end = 202; t22.timetable = [(1, 210)]; t22.status = Tasktory.CLOSE
        self.check(t10+t10,'hoge',1,None,None,None,0,None,0,Tasktory.OPEN)
        self.check(t10+t11,'hoge',1,10,100,101,120,None,0,Tasktory.WAIT)
        self.check(t10+t12,'hoge',1,20,200,202,210,None,0,Tasktory.CLOSE)
        self.check(t10+t20,'hoge',2,None,None,None,0,None,0,Tasktory.OPEN)
        self.check(t10+t21,'hoge',2,10,100,101,120,None,0,Tasktory.WAIT)
        self.check(t10+t22,'hoge',2,20,200,202,210,None,0,Tasktory.CLOSE)

        self.check(t11+t10,'hoge',1,10,100,None,120,None,0,Tasktory.OPEN)
        self.check(t11+t11,'hoge',1,10,100,101,240,None,0,Tasktory.WAIT)
        self.check(t11+t12,'hoge',1,20,100,202,330,None,0,Tasktory.CLOSE)
        self.check(t11+t20,'hoge',2,10,100,None,120,None,0,Tasktory.OPEN)
        self.check(t11+t21,'hoge',2,10,100,101,240,None,0,Tasktory.WAIT)
        self.check(t11+t22,'hoge',2,20,100,202,330,None,0,Tasktory.CLOSE)

        self.check(t12+t10,'hoge',1,20,200,None,210,None,0,Tasktory.OPEN)
        self.check(t12+t11,'hoge',1,10,200,101,330,None,0,Tasktory.WAIT)
        self.check(t12+t12,'hoge',1,20,200,202,420,None,0,Tasktory.CLOSE)
        self.check(t12+t20,'hoge',2,20,200,None,210,None,0,Tasktory.OPEN)
        self.check(t12+t21,'hoge',2,10,200,101,330,None,0,Tasktory.WAIT)
        self.check(t12+t22,'hoge',2,20,200,202,420,None,0,Tasktory.CLOSE)

        self.check(t20+t10,'hoge',2,None,None,None,0,None,0,Tasktory.OPEN)
        self.check(t20+t11,'hoge',2,10,100,None,120,None,0,Tasktory.OPEN)
        self.check(t20+t12,'hoge',2,20,200,None,210,None,0,Tasktory.OPEN)
        self.check(t20+t20,'hoge',2,None,None,None,0,None,0,Tasktory.OPEN)
        self.check(t20+t21,'hoge',2,10,100,101,120,None,0,Tasktory.WAIT)
        self.check(t20+t22,'hoge',2,20,200,202,210,None,0,Tasktory.CLOSE)

        self.check(t21+t10,'hoge',2,10,100,101,120,None,0,Tasktory.WAIT)
        self.check(t21+t11,'hoge',2,10,100,101,240,None,0,Tasktory.WAIT)
        self.check(t21+t12,'hoge',2,10,200,101,330,None,0,Tasktory.WAIT)
        self.check(t21+t20,'hoge',2,10,100,None,120,None,0,Tasktory.OPEN)
        self.check(t21+t21,'hoge',2,10,100,101,240,None,0,Tasktory.WAIT)
        self.check(t21+t22,'hoge',2,20,100,202,330,None,0,Tasktory.CLOSE)

        self.check(t22+t10,'hoge',2,20,200,202,210,None,0,Tasktory.CLOSE)
        self.check(t22+t11,'hoge',2,20,100,202,330,None,0,Tasktory.CLOSE)
        self.check(t22+t12,'hoge',2,20,200,202,420,None,0,Tasktory.CLOSE)
        self.check(t22+t20,'hoge',2,20,200,None,210,None,0,Tasktory.OPEN)
        self.check(t22+t21,'hoge',2,10,200,101,330,None,0,Tasktory.WAIT)
        self.check(t22+t22,'hoge',2,20,200,202,420,None,0,Tasktory.CLOSE)

        # 親／子タスクトリ
        t1 = Tasktory('T', 1); t1.deadline = 100; t1.start = 100;
        t1.end = 100; t1.timetable = [(1, 100)]; t1.status = Tasktory.OPEN
        t11 = Tasktory('T1', 1); t11.deadline = 110; t11.start = 110;
        t11.end = 110; t11.timetable = [(1, 110)]; t11.status = Tasktory.OPEN
        t12 = Tasktory('T2', 1); t12.deadline = 120; t12.start = 120;
        t12.end = 120; t12.timetable = [(1, 120)]; t12.status = Tasktory.OPEN
        t121 = Tasktory('T21', 1); t121.deadline = 121; t121.start = 121;
        t121.end = 121; t121.timetable = [(1, 121)]; t121.status = Tasktory.OPEN
        t2 = Tasktory('T', 2); t2.deadline = 200; t2.start = 200;
        t2.end = 200; t2.timetable = [(1, 200)]; t2.status = Tasktory.WAIT
        t22 = Tasktory('T2', 2); t22.deadline = 220; t22.start = 220;
        t22.end = 220; t22.timetable = [(1, 220)]; t22.status = Tasktory.WAIT
        t221 = Tasktory('T21', 2); t221.deadline = 221; t221.start = 221;
        t221.end = 221; t221.timetable = [(1, 221)]; t221.status = Tasktory.WAIT
        t23 = Tasktory('T3', 2); t23.deadline = 230; t23.start = 230;
        t23.end = 230; t23.timetable = [(1, 230)]; t23.status = Tasktory.WAIT

        t1.append(t11)
        t1.append(t12)
        t12.append(t121)
        t2.append(t22)
        t2.append(t23)
        t22.append(t221)

        t3 = t1 + t2

        self.check(t1,'T',1,100,100,100,100,None,2,Tasktory.OPEN)
        self.check(t11,'T1',1,110,110,110,110,t1,0,Tasktory.OPEN)
        self.check(t12,'T2',1,120,120,120,120,t1,1,Tasktory.OPEN)
        self.check(t121,'T21',1,121,121,121,121,t12,0,Tasktory.OPEN)
        self.check(t2,'T',2,200,200,200,200,None,2,Tasktory.WAIT)
        self.check(t22,'T2',2,220,220,220,220,t2,1,Tasktory.WAIT)
        self.check(t23,'T3',2,230,230,230,230,t2,0,Tasktory.WAIT)
        self.check(t221,'T21',2,221,221,221,221,t22,0,Tasktory.WAIT)

        self.check(t3,'T',2,200,100,200,300,None,3,Tasktory.WAIT)
        self.check(t3['T1'],'T1',1,110,110,110,110,t3,0,Tasktory.OPEN)
        self.check(t3['T2'],'T2',2,220,120,220,340,t3,1,Tasktory.WAIT)
        self.check(t3['T2']['T21'],'T21',2,221,121,221,342,t3['T2'],0,Tasktory.WAIT)
        self.check(t3['T3'],'T3',2,230,230,230,230,t3,0,Tasktory.WAIT)

        # コメント
        t1 = Tasktory('T', 1); t1.comments = "コメント"
        t2 = Tasktory('T', 2); t2.comments = "あいうえお"
        t3 = t1 + t2
        self.assertEqual(t3.comments, "あいうえお")

    #==========================================================================
    # タスクトリメソッド
    #==========================================================================
    def test_get_path(self):
        t1 = Tasktory(1, 'T1', 1)
        self.assertEqual(t1.get_path(), '/T1')
        # TODO
        pass

    def test_get_last_timestamp(self):
        task0 = Tasktory(1, 'task0', 1)
        task1 = Tasktory(2, 'task1', 2)
        task2 = Tasktory(3, 'task2', 3)
        task3 = Tasktory(4, 'task3', 4)
        task0.append(task1)
        task0.append(task2)
        task1.append(task3)
        self.assertEqual(task0.get_last_timestamp(), 4)
        self.assertEqual(task1.get_last_timestamp(), 4)
        self.assertEqual(task2.get_last_timestamp(), 3)

    def test_get_time(self):
        task = Tasktory(1, 'T', 1)
        self.assertEqual(task.get_time(), 0)
        task.add_time(1, 10)
        self.assertEqual(task.get_time(), 10)
        task.add_time(1, 10)
        self.assertEqual(task.get_time(), 20)
        task.timetable = [(1,10)]
        self.assertEqual(task.get_time(), 10)

    def test_get_total_time(self):
        task0 = Tasktory(1, 'task0', 1)
        task1 = Tasktory(2, 'task1', 2)
        task2 = Tasktory(3, 'task2', 3)
        task3 = Tasktory(4, 'task3', 4)
        task0.add_time(1, 1000)
        task1.add_time(2, 2)
        task2.add_time(3, 30)
        task3.add_time(4, 400)
        task0.append(task1)
        task0.append(task2)
        task1.append(task3)
        self.assertEqual(task0.get_total_time(), 1432)
        self.assertEqual(task1.get_total_time(), 402)
        self.assertEqual(task2.get_total_time(), 30)
        self.assertEqual(task3.get_total_time(), 400)

    def test_get_whole_timetable(self):
        # TODO
        pass

    def test_add_time(self):
        t = Tasktory(1, 'hoge', 1)
        self.check(t, 'hoge', 1, None, None, None, 0, None, 0, Tasktory.OPEN)
        t.add_time(1, 10)
        self.check(t, 'hoge', 1, None, 1, None, 10, None, 0, Tasktory.OPEN)
        t.add_time(2, 20)
        self.check(t, 'hoge', 1, None, 1, None, 30, None, 0, Tasktory.OPEN)

    def test_append(self):
        t0 = Tasktory(1, 'task0', 1)
        t1 = Tasktory(2, 'task1', 1)
        t2 = Tasktory(3, 'task2', 1)
        self.check(t0, 'task0', 1, None, None, None, 0, None, 0, Tasktory.OPEN)
        self.check(t1, 'task1', 1, None, None, None, 0, None, 0, Tasktory.OPEN)
        self.check(t2, 'task2', 1, None, None, None, 0, None, 0, Tasktory.OPEN)
        t0.append(t1)
        t0.append(t2)
        self.check(t0, 'task0', 1, None, None, None, 0, None, 2, Tasktory.OPEN)
        self.check(t1, 'task1', 1, None, None, None, 0, t0, 0, Tasktory.OPEN)
        self.check(t2, 'task2', 1, None, None, None, 0, t0, 0, Tasktory.OPEN)

    def test_is_open(self):
        t = Tasktory(1, 'hoge', 1)
        self.assertEqual(t.is_open(), True)
        self.assertEqual(t.is_wait(), False)
        self.assertEqual(t.is_close(), False)

    def test_is_wait(self):
        t = Tasktory(1, 'hoge', 1)
        t.wait()
        self.assertEqual(t.is_open(), False)
        self.assertEqual(t.is_wait(), True)
        self.assertEqual(t.is_close(), False)

    def test_is_close(self):
        t = Tasktory(1, 'hoge', 1)
        t.close()
        self.assertEqual(t.is_open(), False)
        self.assertEqual(t.is_wait(), False)
        self.assertEqual(t.is_close(), True)

    def test_open(self):
        # CLOSE -> OPEN
        t = Tasktory(1, 'hoge', 1)
        t.close()
        self.check(t, 'hoge', 1, None, 1, 1, 0, None, 0, Tasktory.CLOSE)
        t.open()
        self.check(t, 'hoge', 1, None, 1, None, 0, None, 0, Tasktory.OPEN)

        # WAIT -> OPEN
        del t; t = Tasktory(1, 'hoge', 1)
        t.wait()
        self.check(t, 'hoge', 1, None, None, None, 0, None, 0, Tasktory.WAIT)
        t.open()
        self.check(t, 'hoge', 1, None, None, None, 0, None, 0, Tasktory.OPEN)

    def test_wait(self):
        # OPEN -> WAIT
        t = Tasktory(1, 'hoge', 1)
        self.check(t, 'hoge', 1, None, None, None, 0, None, 0, Tasktory.OPEN)
        t.wait()
        self.check(t, 'hoge', 1, None, None, None, 0, None, 0, Tasktory.WAIT)

        # CLOSE -> WAIT
        del t; t = Tasktory(1, 'hoge', 1)
        t.close()
        self.check(t, 'hoge', 1, None, 1, 1, 0, None, 0, Tasktory.CLOSE)
        t.wait()
        self.check(t, 'hoge', 1, None, 1, None, 0, None, 0, Tasktory.WAIT)

    def test_close(self):
        # OPEN -> CLOSE
        t = Tasktory(1, 'hoge', 1)
        self.check(t, 'hoge', 1, None, None, None, 0, None, 0, Tasktory.OPEN)
        t.close()
        self.check(t, 'hoge', 1, None, 1, 1, 0, None, 0, Tasktory.CLOSE)

        # WAIT -> CLOSE
        del t; t = Tasktory(1, 'hoge', 1)
        t.wait()
        self.check(t, 'hoge', 1, None, None, None, 0, None, 0, Tasktory.WAIT)
        t.close()
        self.check(t, 'hoge', 1, None, 1, 1, 0, None, 0, Tasktory.CLOSE)

    def test_get_level(self):
        task0 = Tasktory(1, 'task0', 1)
        task1 = Tasktory(2, 'task1', 2)
        task2 = Tasktory(3, 'task2', 3)
        task3 = Tasktory(4, 'task3', 4)
        task0.append(task1)
        task0.append(task2)
        task1.append(task3)
        self.assertEqual(task0.get_level(), 0)
        self.assertEqual(task1.get_level(), 1)
        self.assertEqual(task2.get_level(), 1)
        self.assertEqual(task3.get_level(), 2)

    def test_copy(self):
        # TODO
        pass

    def test_search(self):
        # TODO
        pass

if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
