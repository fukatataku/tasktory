#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import sys, os
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
COMMON_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', 'common'))
sys.path.append(COMMON_DIR)

import configparser
import datetime
import time

from RWTemplate import RWTemplate
from common import JOURNAL_CONF_FILE, JOURNAL_TMPL_FILE
from common import rexec

class Journal:

    @staticmethod
    def tasktories(journal):
        """ジャーナルテキストを読み込んでタスクトリのリストを返す
        メモがあればそれも返す
        """
        # テンプレートを取得する
        term_tmpl, term_delim, taskline_tmpl = read_config('ReadTemplate')
        return

    @staticmethod
    def journal(tasktory, memo=None):
        """タスクトリからジャーナル用テキストを作成する
        """
        # テンプレートを取得する
        term_tmpl, term_delim, taskline_tmpl = read_config('WriteTemplate')

        # TODO: TMP_TemplateをTemplateに書き込む

        with open(JOURNAL_CONF_FILE, 'r', encoding='utf-8') as f:
            journal_tmpl = f.read()

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
            'OPEN': 'Todo', 'OPENTASKS': tasks[Tasktory.OPEN],
            'WAIT': 'Wait', 'WAITTASKS': tasks[Tasktory.WAIT],
            'CLOSE': 'Done', 'CLOSETASKS': tasks[Tasktory.CLOSE],
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
        term_delim = section['TERM_DELIMITER'].strip("'")
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

