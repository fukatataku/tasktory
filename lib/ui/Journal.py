#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import os, configparser, time, datetime

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
        term_tmpl, term_delim, taskline_tmpl = read_config('ReadTemplate')
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

        return

    @staticmethod
    def tasktory(taskline, term_tmpl, term_delim, taskline_tmpl):
        """タスクラインからタスクトリを生成する
        人間による記述が含まれるので、柔軟に読み取る
        """
        # まずテンプレート通りに読み込んでみる
        # 読み込めない場合は自由記述モードでの読み込む
        # それでもダメならエラー
        try:
            obj = taskline_tmpl.parse(taskline)
        except Exception:
            pass

        # 自由記述モード
        # IDがない場合は新規作成

    @staticmethod
    def journal(tasktory, memo=None):
        """タスクトリからジャーナル用テキストを作成する
        """
        # テンプレートを取得する
        term_tmpl, term_delim, taskline_tmpl = read_config('WriteTemplate')
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
        config.read(JOURNAL_CONF_FILE)
        section = config[section_name]
        term_tmpl = RWTemplate(section['TERM'])
        term_delim = section['TERM_DELIMITER']
        taskline_tmpl = RWTemplate(section['TASKLINE'])
        return term_tmpl, term_delim, taskline_tmpl

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

