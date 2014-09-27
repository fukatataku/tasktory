#!python3
#-*- encoding:utf-8 -*-

import sys, os, datetime, unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory
from lib.ui.Journal import Journal
from lib.common.RWTemplate import RWTemplate

class TestTasktory(unittest.TestCase):

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
        # TODO
        return

    def test_tasktory(self):
        # TODO
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
        # TODO
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
