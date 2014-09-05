#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

# テスト用コード
import sys
sys.path.append('C:/home/fukata/git/tasktory')
#sys.path.append('/Users/taku/git/tasktory')

import os, re, configparser, time, datetime

from lib.core.Tasktory import Tasktory
from lib.common.RWTemplate import RWTemplate
from lib.common.common import rexec
from lib.common.common import JOURNAL_CONF_FILE
from lib.common.common import JOURNAL_READ_TMPL_FILE, JOURNAL_WRITE_TMPL_FILE

class Journal:

    num_reg = re.compile(r'\d+$')
    delim_reg = re.compile(r'([^a-zA-Z0-9_%{}]+)')
    head_reg = re.compile(r'^(%{?YEAR}?[^a-zA-Z0-9_%{}]+)')
    tail_reg = re.compile(r'([^a-zA-Z0-9_%{}]+%{?YEAR}?)$')

    @staticmethod
    def read_config(section_name):
        """コンフィグを読み込んで各種テンプレートを読み込む
        """
        config = configparser.ConfigParser()
        config.read(JOURNAL_CONF_FILE, encoding='utf-8')
        section = config[section_name]

        # 日付テンプレート
        date_tmpl = RWTemplate(section['DATE'])

        # 日付正規表現
        _ = Journal.head_reg.sub(r'(\1)?', section['DATE'])
        _ = Journal.tail_reg.sub(r'(\1)?', _)
        date_reg = re.compile(RWTemplate(_).substitute({
            'YEAR': r'(?P<year>(\d{2})?\d{2})',
            'MONTH': r'(?P<month>\d{1,2})',
            'DAY': r'(?P<day>\d{1,2})'}))

        # 作業時間テンプレート
        time_tmpl = RWTemplate(section['TIME'])

        # 作業時間正規表現
        _ = Journal.delim_reg.sub(r'\s*\1\s*', time_tmpl.template)
        time_reg= re.compile(RWTemplate(_).substitute({
            'SHOUR': r'(?P<shour>\d{1,2})',
            'SMIN': r'(?P<smin>\d{2})',
            'SSEC': r'(?P<ssec>\d{2})',
            'EHOUR': r'(?P<ehour>\d{1,2})',
            'EMIN': r'(?P<emin>\d{2})',
            'ESEC': r'(?P<esec>\d{2})'}))

        # 作業時間リストのデリミタ
        times_delim = section['TIMES_DELIM']

        # タスクラインテンプレート
        taskline_tmpl = RWTemplate(section['TASKLINE'])

        return (date_tmpl, date_reg, time_tmpl, time_reg, times_delim,
                taskline_tmpl)

    @staticmethod
    def tasktories(journal):
        """ジャーナルテキストを読み込んでタスクトリのリストを返す
        メモがあればそれも返す
        """
        # テンプレートを取得する
        config = Journal.read_config('ReadTemplate')
        with open(JOURNAL_READ_TMPL_FILE, 'r', encoding='utf-8') as f:
            journal_tmpl = RWTemplate(f.read().rstrip('\n'))

        # ジャーナルの末尾に改行が無ければ追加する
        #if journal[-1] != '\n': journal += '\n'

        # ジャーナルをパースする
        journal_obj = journal_tmpl.parse(journal)

        # ジャーナルの日付
        year = int(journal_obj['YEAR'])
        month = int(journal_obj['MONTH'])
        day = int(journal_obj['DAY'])
        datestamp = datetime.date(year, month, day).toordinal()

        # タスクライン
        tasks = lambda obj:[o for o in obj.split('\n') if o.strip(' ') != '']
        open_tasklines = tasks(journal_obj['OPENTASKS'])
        wait_tasklines = tasks(journal_obj['WAITTASKS'])
        close_tasklines = tasks(journal_obj['CLOSETASKS'])
        const_tasklines = tasks(journal_obj['CONSTTASKS'])

        # 各タスクラインをタスクトリに変換する
        tsk = lambda t,s:Journal.tasktory(t, config, datestamp, s)
        open_tasks = [tsk(t, Tasktory.OPEN) for t in open_tasklines]
        wait_tasks = [tsk(t, Tasktory.WAIT) for t in wait_tasklines]
        close_tasks = [tsk(t, Tasktory.CLOSE) for t in close_tasklines]
        const_tasks = [tsk(t, Tasktory.CONST) for t in const_tasklines]

        # メモ
        memo = journal_obj['MEMO']

        # 各タスクリストを結合して返す
        return open_tasks + wait_tasks + close_tasks + const_tasks, memo

    @staticmethod
    def tasktory(taskline, config, datestamp, status):
        """タスクラインからタスクトリを生成する
        taskline : ジャーナルテキストから読み出したタスクライン
        config : read_config()で読み出したコンフィグオブジェクト
        datestamp : ジャーナルの日付（グレゴリオ序数）
        status : タスクラインのステータス
        """
        # コンフィグオブジェクトから各要素を取り出す
        (date_tmpl, date_reg, time_tmpl, time_reg, times_delim,
                taskline_tmpl) = config

        # タスクラインをテンプレートに従ってパースする
        taskobj = taskline_tmpl.parse(taskline)

        # タスクトリ名を解決する
        name = os.path.basename(taskobj['PATH'])

        # IDを解決し、タスクトリを作成する
        ID = taskobj['ID']
        task = Tasktory(ID, name)\
                if ID else Manager.tasktory(name)

        # 期日を解決する
        match1 = Journal.num_reg.match(taskobj['DEADLINE'])
        match2 = date_reg.match(taskobj['DEADLINE'])
        if match1:
            deadline = datestamp + int(match1.group())
        elif match2:
            dday = int(match2.group('day'))
            dmonth = int(match2.group('month'))
            if match2.group('year'):
                dyear = int(match2.group('year'))
            else:
                tmpyear = datetime.date.fromordinal(datestamp).year
                tmpline = datetime.date(tmpyear, dmonth, dday).toordinal()
                dyear = tmpyear + (0 if tmpline >= datestamp else 1)
            deadline = datetime.date(dyear, dmonth, dday).toordinal()
        else:
            raise ValueError()
        task.deadline = deadline

        # 作業時間を解決する
        date = datetime.date.fromordinal(datestamp)
        year, month, day = date.year, date.month, date.day
        for t in taskobj['TIMES'].split(times_delim):
            t = t.strip(' ')
            if t == '': continue
            match = time_reg.match(t)
            if not match: raise ValueError()
            shour = int(match.group('shour'))
            smin = int(match.groupdict().get('smin', 0))
            ssec = int(match.groupdict().get('ssec', 0))
            ehour = int(match.group('ehour'))
            emin = int(match.groupdict().get('emin', 0))
            esec = int(match.groupdict().get('esec', 0))
            s = datetime.datetime(year, month, day, shour, smin).timestamp()
            e = datetime.datetime(year, month, day, ehour, emin).timestamp()
            task.add_time(s, e - s)

        # ステータスを設定する
        if status == Tasktory.OPEN:
            task.open()
        elif status == Tasktory.WAIT:
            task.wait()
        elif status == Tasktory.CLOSE:
            task.close()
        elif status == Tasktory.CONST:
            task.const()
        else:
            raise ValueError()

        return task

    @staticmethod
    def journal(date, tasktory, memo=None):
        """タスクトリからジャーナル用テキストを作成する
        date : ジャーナルの日付のdatetime.dateオブジェクト
        tasktory : タスクトリオブジェクト
        """
        # テンプレートを取得する
        config = Journal.read_config('WriteTemplate')
        with open(JOURNAL_WRITE_TMPL_FILE, 'r', encoding='utf-8') as f:
            journal_tmpl = RWTemplate(f.read())

        # TODO: WriteTemplateをReadTemplateに書き込む

        # タスクライン作成
        tasks = {Tasktory.OPEN: '',
                Tasktory.WAIT: '',
                Tasktory.CLOSE: '',
                Tasktory.CONST: ''}

        def regist(node):
            taskline = Journal.taskline(node, config, date)
            nonlocal tasks
            tasks[node.status] += taskline + '\n'
            return

        rexec(tasktory, regist, iter_func=lambda t:t.children,
                iter_sort_func=lambda t:t.ID,
                exec_cond_func=lambda t:not t.is_close(),
                rec_cond_func=lambda t:not t.is_close())

        # ジャーナル作成
        journal = journal_tmpl.substitute({
            'YEAR': date.year, 'MONTH': date.month, 'DAY': date.day,
            'OPENTASKS': tasks[Tasktory.OPEN],
            'WAITTASKS': tasks[Tasktory.WAIT],
            'CLOSETASKS': tasks[Tasktory.CLOSE],
            'CONSTTASKS': tasks[Tasktory.CONST],
            'MEMO': '' if memo is None else memo})

        return journal

    @staticmethod
    def taskline(node, config, date):
        """タスクラインを取得する
        node - Tasktoryオブジェクト
        config - read_config()で得られるコンフィグオブジェクト
        date - ジャーナルの日付のdatetime.dateオブジェクト
        """
        # コンフィグ
        _, _, time_tmpl, _, times_delim, taskline_tmpl = config

        # 残り日数
        rest_days = node.deadline - date.toordinal() if node.deadline else 0

        # 作業時間
        date_epoch = time.mktime(date.timetuple())
        times = times_delim.join(
                [Journal.time_phrase(s,t,time_tmpl) for s,t in node.timetable
                    if s >= date_epoch])

        return taskline_tmpl.substitute({'ID': node.ID,
            'PATH': node.get_path(), 'DEADLINE': rest_days, 'TIMES': times})

    @staticmethod
    def time_phrase(s, t, tmpl):
        """作業時間表現を取得する
        s - 開始日時のエポック秒
        t - 作業時間（秒）
        tmpl - 作業時間表現のRWTemplate
        """
        start = datetime.datetime.fromtimestamp(s)
        end = start + datetime.timedelta(0,t)
        form = lambda n:'{:02}'.format(n)
        return tmpl.substitute({
            'SHOUR': start.hour,
            'SMIN': form(start.minute), 'SSEC': form(start.second),
            'EHOUR': end.hour,
            'EMIN': form(end.minute), 'ESEC': form(end.second)})

def timestamp(year, month, day, hour, minute, sec=0):
    return int(datetime.datetime(year, month, day,
        hour, minute, sec).timestamp())

def datestamp(year, month, day):
    return datetime.date(year, month, day).toordinal()

if __name__ == '__main__':
    journal = """2014/09/05
◆Todo
1:/Project/MyTask @10 [9:00-10:00]
◆Wait

◆Done

◆Const

◆Memo
HOGE
FUGA
"""
    tasks, memo = Journal.tasktories(journal)
    for tsk in tasks:
        print("===", tsk.ID, "===")
        print("Name :", tsk.name)
        print("Dead :", datetime.date.fromordinal(tsk.deadline))
        for s,t in tsk.timetable:
            start = datetime.datetime.fromtimestamp(s)
            end = datetime.datetime.fromtimestamp(s + t)
            print("Time :", start, "-", end)
    #t1 = Tasktory(1, 'Project')
    #t1.deadline = datestamp(2014, 9, 5)
    #t1.add_time(timestamp(2014,9,5,9,0,0), 3600)
    #t1.add_time(timestamp(2014,9,5,10,0,0), 3600)

    #t11 = Tasktory(2, 'TaskA')
    #t11.deadline = datestamp(2014, 9, 5)
    #t11.add_time(timestamp(2014,9,4,9,0,0), 3600)
    #t1.append(t11)
    #journal = Journal.journal(t1)
    #print(journal)
    pass
