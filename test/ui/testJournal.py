#!C:/python/python3.4/python
#!python3
#-*- encoding:utf-8 -*-

import sys, os, datetime, unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory
from lib.ui.Journal import Journal
from lib.common.RWTemplate import RWTemplate

OPEN = Tasktory.OPEN
WAIT = Tasktory.WAIT
CLOSE = Tasktory.CLOSE
CONST = Tasktory.CONST

class TestTasktory(unittest.TestCase):

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

    def test_date_regex(self):
        r = r'%YEAR/%MONTH/%DAY'
        p = r'^((?P<year>(\d{2})?\d{2})/)?(?P<month>\d{1,2})/(?P<day>\d{1,2})$'
        reg = Journal.date_regex(r)
        self.assertEqual(reg.pattern, p)
        self.assertTrue(bool(reg.match('2014/04/01')))
        self.assertTrue(bool(reg.match('2014/4/1')))
        self.assertTrue(bool(reg.match('14/4/1')))
        self.assertTrue(bool(reg.match('4/1')))
        self.assertFalse(bool(reg.match('2014/04/01/01')))
        self.assertFalse(bool(reg.match('20014/04/01')))
        self.assertFalse(bool(reg.match('2014/004/01')))
        self.assertFalse(bool(reg.match('2014/04/001')))
        self.assertFalse(bool(reg.match('4/04/01')))
        self.assertFalse(bool(reg.match('14//01')))

        r = r'%{YEAR}-%{MONTH}-%{DAY}'
        p = r'^((?P<year>(\d{2})?\d{2})-)?(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
        reg = Journal.date_regex(r)
        self.assertEqual(reg.pattern, p)
        self.assertTrue(bool(reg.match('2014-04-01')))
        self.assertTrue(bool(reg.match('2014-4-1')))
        self.assertTrue(bool(reg.match('14-4-1')))
        self.assertTrue(bool(reg.match('4-1')))

        r = r'%MONTH/%DAY/%YEAR'
        p = r'^(?P<month>\d{1,2})/(?P<day>\d{1,2})(/(?P<year>(\d{2})?\d{2}))?$'
        reg = Journal.date_regex(r)
        self.assertEqual(reg.pattern, p)
        self.assertTrue(bool(reg.match('04/01/2014')))
        self.assertDictEqual(reg.match('04/01/2014').groupdict(),
                {'year': '2014', 'month': '04', 'day': '01'})
        self.assertTrue(bool(reg.match('4/1/14')))
        self.assertDictEqual(reg.match('4/1/14').groupdict(),
                {'year': '14', 'month': '4', 'day': '1'})
        self.assertTrue(bool(reg.match('4/1')))
        self.assertDictEqual(reg.match('4/1').groupdict(),
                {'year': None, 'month': '4', 'day': '1'})

        r = r'%MONTH/%YEAR/%DAY'
        p = r'^(?P<month>\d{1,2})/(?P<year>(\d{2})?\d{2})/(?P<day>\d{1,2})$'
        reg = Journal.date_regex(r)
        self.assertEqual(reg.pattern, p)
        self.assertTrue(bool(reg.match('04/2014/01')))
        self.assertTrue(bool(reg.match('4/14/1')))
        self.assertFalse(bool(reg.match('4/1')))
        return

    def test_time_regex(self):
        r = r'%SHOUR:%SMIN:%SSEC-%EHOUR:%EMIN:%ESEC'
        p = r'^(?P<shour>\d{1,2})\s*:\s*(?P<smin>\d{2})\s*:\s*(?P<ssec>\d{2})\s*-\s*(?P<ehour>\d{1,2})\s*:\s*(?P<emin>\d{2})\s*:\s*(?P<esec>\d{2})$'
        reg = Journal.time_regex(r)
        self.assertEqual(reg.pattern, p)
        self.assertTrue(bool(reg.match('00:00:00-12:34:56')))
        self.assertTrue(bool(reg.match('0:00:00-2:34:56')))
        self.assertTrue(bool(reg.match('00 : 00 : 00  -  2 : 34 : 56')))
        m = reg.match('00 : 00 : 00  -  12 : 34 : 56')
        self.assertDictEqual(m.groupdict(), {'shour': '00', 'smin': '00',
            'ssec': '00', 'ehour': '12', 'emin': '34', 'esec': '56'})

        r = r'%SHOUR:%SMIN-%EHOUR:%EMIN'
        p = r'^(?P<shour>\d{1,2})\s*:\s*(?P<smin>\d{2})\s*-\s*(?P<ehour>\d{1,2})\s*:\s*(?P<emin>\d{2})$'
        reg = Journal.time_regex(r)
        self.assertEqual(reg.pattern, p)
        self.assertTrue(bool(reg.match('00:00-12:34')))
        return

    def test_tasktories(self):
        j_tmpl ="""%YEAR/%MONTH/%DAY
$ Todo
%OPENTASKS
$ Wait
%WAITTASKS
$ Done
%CLOSETASKS
$ Const
%CONSTTASKS
$ MEMO
%MEMO
"""
        j_tmpl = RWTemplate(j_tmpl)
        tl_tmpl = RWTemplate('%PATH @%DEADLINE [%TIMES]')
        date_reg = Journal.date_regex(r'%YEAR/%MONTH/%DAY')
        time_reg = Journal.time_regex('%SHOUR:%SMIN-%EHOUR:%EMIN')
        tm_delim = ','
        stamp = datetime.date(2014, 4, 1).toordinal()
        tstamp = datetime.datetime(2014, 4, 1, 0, 0, 0).timestamp()

        # 空のジャーナル
        journal = """2014/04/01
$ Todo

$ Wait

$ Done

$ Const

$ MEMO

"""
        tasks, memo = Journal.tasktories(journal,
                j_tmpl, tl_tmpl, date_reg, time_reg, tm_delim)
        self.assertListEqual(tasks, [])
        self.assertEqual(memo, '')

        # 空でないジャーナル
        journal = """2014/04/01
$ Todo
/ @365 []
# Root Tasktory
/Project @30 []
 # Project Tasktory
/Project/Task1 @3 [0:00-1:00]
 # あいうえお
 # かきくけこ
 # さしすせそ
/Project/Task2 @3 [1:00-2:00, 4:00-5:00]
$ Wait

$ Done
/Project/Task3 @0 [2:00-4:00]
$ Const
/Project/ConstTask @365 [5:00-10:00]
$ MEMO
This is memo
hogehoge
"""
        tasks, memo = Journal.tasktories(journal,
                j_tmpl, tl_tmpl, date_reg, time_reg, tm_delim)
        def fullpath(t): return fullpath(t.children[0]) if t.children else t.path()
        tasks = sorted(tasks, key=fullpath)
        def foot(t): return foot(t) if t.children else t
        self.check(tasks[0], '', stamp+365, None, OPEN, None, 'Root Tasktory')
        self.assertListEqual(tasks[0].children, [])

        self.check(tasks[1], '', None, None, OPEN, None, '')
        self.check(tasks[1].children[0], 'Project', stamp+30,
                tasks[1], OPEN, None, 'Project Tasktory')
        self.assertListEqual(tasks[1].children[0].children, [])

        self.check(tasks[2], '', None, None, CONST, None, '')
        self.check(tasks[2].children[0], 'Project', None, tasks[2], CONST, None, '')
        self.check(tasks[2].children[0].children[0], 'ConstTask', stamp+365,
                tasks[2].children[0], CONST, None, '')

        self.check(tasks[3], '', None, None, OPEN, None, '')
        self.check_time(tasks[3])
        self.check(tasks[3].children[0], 'Project', None, tasks[3], OPEN, None, '')
        self.check_time(tasks[3].children[0])
        self.check(tasks[3].children[0].children[0], 'Task1', stamp+3,
                tasks[3].children[0], OPEN, None, 'あいうえお\nかきくけこ\nさしすせそ')
        self.check_time(tasks[3].children[0].children[0], (tstamp, 3600))

        self.check(tasks[4], '', None, None, OPEN, None, '')
        self.check(tasks[4].children[0], 'Project', None, tasks[4], OPEN, None, '')
        self.check(tasks[4].children[0].children[0], 'Task2', stamp+3,
                tasks[4].children[0], OPEN, None, '')

        self.check(tasks[5], '', None, None, CLOSE, None, '')
        self.check(tasks[5].children[0], 'Project', None, tasks[5], CLOSE, None, '')
        self.check(tasks[5].children[0].children[0], 'Task3', stamp+0,
                tasks[5].children[0], CLOSE, None, '')

        self.assertEqual(memo, 'This is memo\nhogehoge')
        return

    def test_tasktory(self):
        date = datetime.date(2014, 4, 1)
        datestamp = date.toordinal()
        timestamp = datetime.datetime(2014, 4, 1, 0, 0, 0).timestamp()
        tl_tmpl = RWTemplate('%PATH @%DEADLINE [%TIMES]')
        date_reg = Journal.date_regex(r'%YEAR/%MONTH/%DAY')
        tm_tmpl = RWTemplate('%SHOUR:%SMIN-%EHOUR:%EMIN')
        time_reg = Journal.time_regex('%SHOUR:%SMIN-%EHOUR:%EMIN')
        tm_delim = ','

        # 空タスクトリ
        tl = '/ @0 []'
        t = Journal.tasktory(date, OPEN, tl,
                tl_tmpl, date_reg, time_reg, tm_delim)
        self.check(t, '', datestamp, None, OPEN, None, '')
        self.check_child(t)
        self.check_time(t)

        # 名前付き
        tl = '#123.あいうえお @2014/05/01 [0:00-10:00]'
        t = Journal.tasktory(date, Tasktory.WAIT, tl,
                tl_tmpl, date_reg, time_reg, tm_delim)
        self.check(t, '#123.あいうえお', datestamp + 30, None, WAIT, None, '')
        self.check_child(t)
        self.check_time(t, (timestamp, 36000))

        tl = '#123.あいうえお @14/5/1 [0:00-1:00, 2:00-3:00]'
        t = Journal.tasktory(date, Tasktory.WAIT, tl,
                tl_tmpl, date_reg, time_reg, tm_delim)
        self.check(t, '#123.あいうえお', datestamp + 30, None, WAIT, None, '')
        self.check_child(t)
        self.check_time(t, (timestamp, 3600), (timestamp+7200, 3600))

        tl = '/#123.あいうえお @5/1 [0:00-1:00]'
        t = Journal.tasktory(date, Tasktory.CONST, tl,
                tl_tmpl, date_reg, time_reg, tm_delim)
        self.check(t, '', None, None, CONST, None, '')
        self.check_time(t)
        t1 = t.children[0]
        self.check(t1, '#123.あいうえお', datestamp + 30, t, CONST, None, '')
        self.check_child(t1)
        self.check_time(t1, (timestamp, 3600))

        # 失敗
        tl = ''
        self.assertRaises(ValueError, Journal.tasktory, date, Tasktory.WAIT,
                tl, tl_tmpl, date_reg, time_reg, tm_delim)
        try:
            t = Journal.tasktory(date, Tasktory.WAIT, tl,
                    tl_tmpl, date_reg, time_reg, tm_delim)
        except ValueError as e:
            self.assertEqual(e.args[0], '')

        tl = '/'
        self.assertRaises(ValueError, Journal.tasktory, date, Tasktory.WAIT,
                tl, tl_tmpl, date_reg, time_reg, tm_delim)
        try:
            t = Journal.tasktory(date, Tasktory.WAIT, tl,
                    tl_tmpl, date_reg, time_reg, tm_delim)
        except ValueError as e:
            self.assertEqual(e.args[0], '/')

        return

    def test_deadline(self):
        date = datetime.date(2014, 4, 1)
        date_reg = Journal.date_regex(r'%YEAR/%MONTH/%DAY')
        # 普通
        self.assertEqual(Journal.deadline(date, '2014/05/01', date_reg),
                datetime.date(2014, 5, 1).toordinal())

        # 桁省略
        self.assertEqual(Journal.deadline(date, '14/5/1', date_reg),
                datetime.date(2014, 5, 1).toordinal())
        self.assertEqual(Journal.deadline(date, '14/3/1', date_reg),
                datetime.date(2114, 3, 1).toordinal())
        self.assertEqual(Journal.deadline(date, '0014/3/1', date_reg),
                datetime.date(14, 3, 1).toordinal())

        # 誤り
        self.assertRaises(ValueError,
                Journal.deadline, date, '014/4/1', date_reg)

        # 年数省略
        self.assertEqual(Journal.deadline(date, '5/1', date_reg),
                datetime.date(2014, 5, 1).toordinal())
        self.assertEqual(Journal.deadline(date, '3/1', date_reg),
                datetime.date(2015, 3, 1).toordinal())

        # 残り日数表示
        self.assertEqual(Journal.deadline(date, '0', date_reg),
                datetime.date(2014, 4, 1).toordinal())
        self.assertEqual(Journal.deadline(date, '1', date_reg),
                datetime.date(2014, 4, 2).toordinal())
        return

    def test_timetable(self):
        date = datetime.date(2014, 4, 1)
        time_reg = Journal.time_regex('%SHOUR:%SMIN-%EHOUR:%EMIN')
        times_delim = ','
        timetable = lambda s:Journal.timetable(date, s, time_reg, times_delim)
        stamp = int(datetime.datetime(2014, 4, 1, 0, 0, 0).timestamp())

        self.assertListEqual(timetable(''), [])
        self.assertListEqual(timetable('0:00-1:00'), [(stamp, 3600)])
        self.assertListEqual(timetable('0:00-0:00'), [(stamp, 0)])
        self.assertListEqual(timetable('0:00 - 1:00  ,  1:00- 10:00  '),
                [(stamp, 3600), (stamp+3600, 32400)])
        return

    def test_journal(self):
        j_tmpl ="""%YEAR/%MONTH/%DAY
$ Todo
%OPENTASKS
$ Wait
%WAITTASKS
$ Done
%CLOSETASKS
$ Const
%CONSTTASKS
$ MEMO
%MEMO
"""
        date = datetime.date(2014, 4, 1)
        j_tmpl = RWTemplate(j_tmpl)
        tl_tmpl = RWTemplate('%PATH @%DEADLINE [%TIMES]')
        tm_tmpl = RWTemplate('%SHOUR:%SMIN-%EHOUR:%EMIN')
        tm_delim = ','
        stamp = datetime.date(2014, 4, 1).toordinal()
        tstamp = datetime.datetime(2014, 4, 1, 0, 0, 0).timestamp()

        # None
        self.assertRaises(TypeError, Journal.journal,
            date, None, '', j_tmpl, tl_tmpl, tm_tmpl, tm_delim, 365)

        # 出力タスクトリなし
        root = Tasktory('', stamp + 366)
        j = Journal.journal(date, root, '',
                j_tmpl, tl_tmpl, tm_tmpl, tm_delim, 365)
        journal = """2014/04/01
$ Todo

$ Wait

$ Done

$ Const

$ MEMO

"""
        self.assertEqual(j, journal)

        # タスクトリ
        root = Tasktory('', stamp + 366); root.comments += 'Root task'
        proj = Tasktory('Project', stamp + 30); proj.comments += 'Project task'
        root.append(proj)
        task1 = Tasktory('Task1', stamp + 3).add_time(tstamp, 3600)
        task1.comments = 'task1\nほげほげ'
        proj.append(task1)
        task2 = Tasktory('Task2', stamp + 3).add_time(
                tstamp+3600, 3600).add_time(tstamp+10800, 3600)
        proj.append(task2)
        task3 = Tasktory('Task3', stamp + 0, CLOSE).add_time(tstamp+7200, 3600)
        proj.append(task3)
        ctask = Tasktory('ConstTask', stamp + 365, CONST).add_time(tstamp+14400, 3600)
        proj.append(ctask)

        j = Journal.journal(date, root, 'This is memo\nhogehoge',
                j_tmpl, tl_tmpl, tm_tmpl, tm_delim, 365)

        journal = """2014/04/01
$ Todo
/Project @30 []
 # Project task
/Project/Task1 @3 [0:00-1:00]
 # task1
 # ほげほげ
/Project/Task2 @3 [1:00-2:00,3:00-4:00]

$ Wait

$ Done

$ Const
/Project/ConstTask @365 [4:00-5:00]

$ MEMO
This is memo
hogehoge
"""
        self.assertEqual(j, journal)
        return

    def test_taskline(self):
        date = datetime.date(2014, 4, 1)
        datestamp = date.toordinal()
        timestamp = int(datetime.datetime(2014, 4, 1).timestamp())
        tl_tmpl = RWTemplate('%PATH @%DEADLINE [%TIMES]')
        tm_tmpl = RWTemplate('%SHOUR:%SMIN-%EHOUR:%EMIN')
        tm_delim = ','

        # 空タスクトリ
        t = Tasktory('', datestamp + 3650)
        self.assertEqual(Journal.taskline(date, t, tl_tmpl, tm_tmpl, tm_delim),
                '/ @3650 []')

        # 名前付き
        t1 = Tasktory('#123.あいうえお', datestamp + 30)
        self.assertEqual(Journal.taskline(date, t1, tl_tmpl, tm_tmpl, tm_delim),
                '/#123.あいうえお @30 []')
        t.append(t1)
        t1.add_time(timestamp, 3600)
        self.assertEqual(Journal.taskline(date, t1, tl_tmpl, tm_tmpl, tm_delim),
                '/#123.あいうえお @30 [0:00-1:00]')

        t11 = Tasktory('かきくけこ', datestamp + 15)
        self.assertEqual(Journal.taskline(date, t11, tl_tmpl, tm_tmpl, tm_delim),
                '/かきくけこ @15 []')
        t1.append(t11)
        t11.add_time(timestamp+3600, 1800)
        t11.add_time(timestamp+36000, 7200)
        self.assertEqual(Journal.taskline(date, t11, tl_tmpl, tm_tmpl, tm_delim),
                '/#123.あいうえお/かきくけこ @15 [1:00-1:30,10:00-12:00]')
        return

    def test_time_phrase(self):
        stamp = datetime.datetime(2014, 4, 1, 0, 0, 0).timestamp()
        tmpl = RWTemplate('%SHOUR:%SMIN:%SSEC-%EHOUR:%EMIN:%ESEC')
        self.assertEqual(Journal.time_phrase(stamp, 3600, tmpl),
                '0:00:00-1:00:00')
        tmpl = RWTemplate('%SHOUR:%SMIN-%EHOUR:%EMIN')
        self.assertEqual(Journal.time_phrase(stamp, 3600, tmpl),
                '0:00-1:00')
        return


if __name__ == '__main__':
    print(datetime.datetime.now())
    unittest.main()
