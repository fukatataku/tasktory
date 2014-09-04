#!python3
# -*- encoding:utf-8 -*-

# テスト用コード
import sys
#sys.path.append('C:/home/fukata/git/tasktory')
sys.path.append('/Users/taku/git/tasktory')

import os, re, configparser, time, datetime

from lib.core.Tasktory import Tasktory
from lib.common.RWTemplate import RWTemplate
from lib.common.common import rexec
from lib.common.common import JOURNAL_CONF_FILE
from lib.common.common import JOURNAL_READ_TMPL_FILE, JOURNAL_WRITE_TMPL_FILE

class Journal:

    @staticmethod
    def tasktories(journal):
        """ジャーナルテキストを読み込んでタスクトリのリストを返す
        メモがあればそれも返す
        """
        # テンプレートを取得する
        config = read_config('ReadTemplate')
        with open(JOURNAL_READ_TMPL_FILE, 'r', encoding='utf-8') as f:
            journal_tmpl = f.read()

        # ジャーナルをパースする
        obj = journal_tmpl.parse(journal)

        # タイムスタンプ
        year = int(obj['YEAR'])
        month = int(obj['MONTH'])
        day = int(obj['DAY'])
        timestamp = datetime.date(year, month, day).toordinal()

        # タスクライン
        tasks = lambda obj:[o for o in obj.split('\n') if o != '']
        open_tasklines = tasks(obj['OPENTASKS'])
        wait_tasklines = tasks(obj['WAITTASKS'])
        close_tasklines = tasks(obj['CLOSETASKS'])

        # 各タスクラインをタスクトリに変換する
        tsk = lambda t,s:tasktory(t, config, timestamp, s)
        open_tasks = [tsk(t, Tasktory.OPEN) for t in open_tasklines]
        wait_tasks = [tsk(t, Tasktory.WAIT) for t in wait_tasklines]
        close_tasks = [tsk(t, Tasktory.CLOSE) for t in close_tasklines]

        # 各タスクリストを結合して返す
        return open_tasks + wait_tasks + close_tasks

    @staticmethod
    def tasktory(taskline, config, timestamp, status):
        """タスクラインからタスクトリを生成する
        テンプレートに沿って読み出す
        DEADLINEについては以下のルールで読み出す
        要素が３つあった場合は年月日（2014/4/1）
        ２つの場合は月日（4/1）
        １つの場合は残り日数（１）
        いずれの場合でも変更できるようにする
        """
        (date_tmpl, term_tmpl, term_delim, taskline_tmpl) = config

        obj = taskline_tmpl.parse(taskline)
        print(obj)
        # タスクトリ名を解決する
        name = os.path.basename(obj['PATH'])
        print(name)

        # IDを解決する
        if obj['ID']:
            # 既存のタスクトリ
            pass
        else:
            # 新しいタスクトリを作成する
            pass

        # 期日を解決する
        num = re.compile(r'\d+$')
        match = num.match(obj['DEADLINE'])
        if match:
            days = int(match.group())
            print(days)
        head = re.compile(r'^(%{?YEAR}?[^a-zA-Z0-9_%{}]+)')
        tail = re.compile(r'([^a-zA-Z0-9_%{}]+%{?YEAR}?)$')
        date_reg = head.sub(r'(\1)?', date_tmpl.template)
        date_reg = tail.sub(r'(\1)?', date_reg)
        date_reg = RWTemplate(date_reg).substitute({
            'YEAR': r'(?P<year>(\d{2})?\d{2})',
            'MONTH': r'(?P<month>\d{1,2})',
            'DAY': r'(?P<day>\d{1,2})'})
        date_reg = re.compile(date_reg)
        match = date_reg.match(obj['DEADLINE'])
        if match:
            year = int(match.group('year'))
            year = year if year is not None else 2014
            month = int(match.group('month'))
            day = int(match.group('day'))
            print(year, month, day)

        # 作業時間を解決する
        delim = re.compile(r'([^a-zA-Z0-9_%{}]+)')
        term_reg = delim.sub(r'\s*\1\s*', term_tmpl.template)
        term_reg= RWTemplate(term_reg).substitute({
            'SHOUR': r'(?P<shour>\d{1,2})',
            'SMIN': r'(?P<smin>\d{2})',
            'EHOUR': r'(?P<ehour>\d{1,2})',
            'EMIN': r'(?P<emin>\d{2})'})
        term_reg = re.compile(term_reg)
        for t in obj['TERMS'].split(term_delim):
            t = t.strip(' ')
            match = term_reg.match(t)
            if match:
                shour = int(match.group('shour'))
                smin = int(match.group('smin'))
                ehour = int(match.group('ehour'))
                emin = int(match.group('emin'))
                print(shour, smin, ehour, emin)

        return

    @staticmethod
    def stat(task, status):
        """タスクトリのステータスを設定する
        """
        if status == Tasktory.OPEN:
            task.open()
        elif status == Tasktory.WAIT:
            task.wait()
        elif status == Tasktory.CLOSE:
            task.close()
        else:
            raise ValueError()
        return

    @staticmethod
    def journal(tasktory, memo=None):
        """タスクトリからジャーナル用テキストを作成する
        """
        # テンプレートを取得する
        (date_tmpl, term_tmpl, term_delim,
                taskline_tmpl) = read_config('WriteTemplate')
        with open(JOURNAL_WRITE_TMPL_FILE, 'r', encoding='utf-8') as f:
            journal_tmpl = RWTemplate(f.read())

        # TODO: TMP_TemplateをTemplateに書き込む

        # 日付
        today = datetime.date.today()

        # タスクライン
        # TODO: ツリー構造に則って並べるかどうか決める

        # TODO: ツリー構造を保つ場合はこっち
        #tasks = {Tasktory.OPEN: '',
        #        Tasktory.WAIT: '',
        #        Tasktory.CLOSE: ''}

        #def regist(node):
        #    taskline = taskline(node, term_tmpl, term_delim,
        #            taskline_tmpl, today)
        #    nonlocal tasks
        #    tasks[node.status] += taskline + '\n'
        #    return

        #rexec(tasktory, regist, iter_func=lambda t:t.children,
        #        iter_sort_func=lambda t:t.deadline,
        #        exec_cond_func=lambda t:t.status != Tasktory.CLOSE,
        #        rec_cond_func=lambda t:t.status != Tasktory.CLOSE)

        # TODO: ツリー構造を捨てる場合はこっち
        # タスクトリを直列化
        tasktories = list(tasktory)

        # フィルターを掛ける
        open_tasks = [t for t in tasktories if t.status == Tasktory.OPEN]
        wait_tasks = [t for t in tasktories if t.status == Tasktory.WAIT]

        # ソートする
        # TODO: ソートの基準を決める
        open_tasks = sorted(open_tasks, key=lambda t:t.deadline)
        wait_tasks = sorted(wait_tasks, key=lambda t:t.deadline)

        # タスクラインに変換する
        tl = lambda t:taskline(t, term_tmpl, term_delim, taskline_tmpl, today)
        open_tasks = '\n'.join([tl(t) for t in open_tasks])
        wait_tasks = '\n'.join([tl(t) for t in wait_tasks])

        # テンプレートにデータを埋め込む
        journal = journal_tmpl.substitute({
            'YEAR': today.year, 'MONTH': today.month, 'DAY': today.day,
            'OPENTASKS': tasks[Tasktory.OPEN],
            'WAITTASKS': tasks[Tasktory.WAIT],
            'CLOSETASKS': tasks[Tasktory.CLOSE],
            'MEMO': '' if memo is None else memo})

        return journal

    @staticmethod
    def read_config(section_name):
        """コンフィグを読み込んで各種テンプレートを読み込む
        """
        config = configparser.ConfigParser()
        config.read(JOURNAL_CONF_FILE, encoding='utf-8')
        section = config[section_name]
        date_tmpl = RWTemplate(section['DATE'])
        term_tmpl = RWTemplate(section['TERM'])
        term_delim = section['TERM_DELIMITER']
        taskline_tmpl = RWTemplate(section['TASKLINE'])
        return date_tmpl, term_tmpl, term_delim, taskline_tmpl

    @staticmethod
    def taskline(node, term_tmpl, term_delim, taskline_tmpl, date):
        """タスクラインを取得する
        node - Tasktoryオブジェクト
        term_tmpl - 作業時間表現のRWTemplate
        term_delim - 作業時間表現のデリミタ
        taskline_tmpl - タスクライン表現のRWTemplate
        date - datetime.date.today()
        """
        # 残り日数
        rest_days = node.deadline - date.toordinal()

        # 作業時間
        epoch = time.mktime(date.timetuple())
        terms = term_delim.join(
                [term(s,t,term_tmpl) for s,t in node.timetable if s >= epoch])

        return taskline_tmpl.substitute({
            'ID': node.ID,
            'PATH': node.get_path(),
            'REST_DAYS': rest_days,
            'TERMS': terms})

    @staticmethod
    def term(s, t, tmpl):
        """作業時間を取得する
        s - 開始日時のエポック秒
        t - 作業時間（秒）
        tmpl - 作業時間表現のRWTemplate
        """
        shour, smin, ssec = parse_sec(s - epoch)
        ehour, emin, esec = parse_sec(s + t - epoch)
        bhour, bmin, bsec = parse_sec(t)
        return tmpl.substitute({
            'SHOUR': shour, 'SMIN': smin, 'SSEC': ssec,
            'EHOUR': ehour, 'EMIN': emin, 'ESEC': esec,
            'BHOUR': bhour, 'BMIN': bmin, 'BSEC': bsec})

    @staticmethod
    def parse_sec(total_sec):
        """秒を時分秒に変換する
        """
        hour = total_sec // 3600; total_sec %= 3600
        minute = total_sec // 60; total_sec %= 60
        second = total_sec
        return hour, minute, second

if __name__ == '__main__':
    taskline = ':/project/task @2014/9/6 [9:00-12:00, 13:00 - 17:45]'
    config = Journal.read_config('ReadTemplate')
    Journal.tasktory(taskline, config, 1, Tasktory.OPEN)
    pass
