# -*- encoding:utf-8 -*-

import os, re, datetime, time

from lib.common.RWTemplate import RWTemplate
from lib.core.Tasktory import Tasktory

# 定数
OPEN = Tasktory.OPEN
WAIT = Tasktory.WAIT
CLOSE = Tasktory.CLOSE
CONST = Tasktory.CONST

class Journal:

    inf_reg = re.compile(r'^inf$', re.I)
    num_reg = re.compile(r'-?\d+$')
    head_reg = re.compile(r'^(%{?YEAR}?[^a-zA-Z0-9_%{}]+)')
    tail_reg = re.compile(r'([^a-zA-Z0-9_%{}]+%{?YEAR}?)$')
    delim_reg = re.compile(r'([^a-zA-Z0-9_%{}]+)')

    path_reg = re.compile(r'^(?:/[^\\/:*?"<>|\s]*)+$', re.M)

    #==========================================================================
    # 正規表現生成メソッド
    #==========================================================================
    @staticmethod
    def date_regex(tmpl_str):
        """日付テンプレート文字列から日付正規表現を作成する
        年数はあっても無くても良いようにする
        """
        _ = Journal.head_reg.sub(r'(\1)?', tmpl_str)
        _ = Journal.tail_reg.sub(r'(\1)?', _)
        _ = r'^' + _ + r'$'
        return re.compile(RWTemplate(_).substitute({
            'YEAR': r'(?P<year>(\d{2})?\d{2})',
            'MONTH': r'(?P<month>\d{1,2})',
            'DAY': r'(?P<day>\d{1,2})'}))

    @staticmethod
    def time_regex(tmpl_str):
        """作業時間テンプレート文字列から作業時間正規表現を作成する
        空白が含まれていても良いようにする
        """
        _ = Journal.delim_reg.sub(r'\s*\1\s*', tmpl_str)
        _ = r'^' + _ + r'$'
        return re.compile(RWTemplate(_).substitute({
            'SHOUR': r'(?P<shour>\d{1,2})',
            'SMIN': r'(?P<smin>\d{2})',
            'SSEC': r'(?P<ssec>\d{2})',
            'EHOUR': r'(?P<ehour>\d{1,2})',
            'EMIN': r'(?P<emin>\d{2})',
            'ESEC': r'(?P<esec>\d{2})'}))

    #==========================================================================
    # ジャーナル → タスクトリ変換メソッド
    #==========================================================================
    @staticmethod
    def tasktories(journal, journal_tmpl, taskline_tmpl,
            date_reg, time_reg, times_delim, infinite):
        """ジャーナルテキストを読み込んでパスとタスクトリのペアのリストを返す
        メモがあればそれも返す
        """
        # ジャーナルをパースする
        journal_dict = journal_tmpl.parse(journal)

        # ジャーナルの日付
        date = datetime.date(
                int(journal_dict['YEAR']),
                int(journal_dict['MONTH']),
                int(journal_dict['DAY']))

        # タスクライン
        tasklines = {}
        statuses = (OPEN, WAIT, CLOSE, CONST)
        keys = ('OPENTASKS', 'WAITTASKS', 'CLOSETASKS', 'CONSTTASKS')
        for s, k in zip(statuses, keys):
            tasklines[s] = [tl for tl in journal_dict[k].split('\n')
                    if tl.strip(' ') != '']

        # 各タスクラインをタスクトリに変換する
        tasks = {}
        for key, tls in tasklines.items():
            tasks[key] = []

            # タスクトリまたはコメント
            _ = [tl.lstrip(' ')[1:].lstrip(' ') if tl.lstrip(' ')[0] == '#'
                    else Journal.tasktory(
                        date, key, tl, taskline_tmpl, date_reg,
                        time_reg, times_delim, infinite) for tl in tls]

            # コメントをタスクトリに格納する
            prev = None
            for v in _:
                if isinstance(v, Tasktory):
                    tasks[key].append(v)
                    prev = Journal.foot(v)
                elif v is not None and prev is not None:
                    prev.comments += ('' if prev.comments == '' else '\n') + v
                else:
                    continue

        # メモ
        memo = journal_dict['MEMO']

        # 各タスクリストを結合して返す
        return sum(tasks.values(), []), memo

    @staticmethod
    def tasktory(date, status, taskline,
            taskline_tmpl, date_reg, time_reg, times_delim, infinite):
        """タスクラインからタスクトリを生成したタスクトリを返す
        date : ジャーナルの日付（datetime.dateオブジェクト）
        status : タスクラインのステータス
        taskline : ジャーナルテキストから読み出したタスクライン
        """
        # タスクラインをテンプレートに従ってパースする
        taskdict = taskline_tmpl.parse(taskline)

        # タスクトリリストを作成する
        _ = [Tasktory(n, None, None)
                for n in taskdict['PATH'].rstrip('/').split('/')]

        # 期日を解決する
        _[-1].deadline = Journal.deadline(
                date, taskdict['DEADLINE'], date_reg, infinite)

        # ステータスを解決する
        _[-1].status = status

        # 作業時間を解決する
        tb = Journal.timetable(date, taskdict['TIMES'], time_reg, times_delim)
        for s,t in tb: _[-1].add_time(s,t)

        # 中間タスクのコメントをNoneにする
        for n in _[0:-1]:
            n.comments = None

        # タスクトリリストを直列化
        task = _[0]
        tail = task
        for t in _[1:]:
            tail.append(t)
            tail = t

        return task

    @staticmethod
    def foot(task):
        # 直列タスクトリの末端にアクセスする
        return Journal.foot(task.children[0]) if task.children else task

    @staticmethod
    def deadline(date, string, date_reg, infinite):
        """タスクラインパース結果から期日を取得する
        """
        # 無期限の場合は・・・
        match0 = Journal.inf_reg.match(string)
        if match0: return date.toordinal() + 2 * infinite

        # 数値が１つだけの場合は残り日数として解釈する
        match1 = Journal.num_reg.match(string)
        if match1: return date.toordinal() + int(match1.group())

        match2 = date_reg.match(string)
        if not match2: raise ValueError()

        # 数値が２つ以上の場合は日付として解釈する
        day = int(match2.group('day'))
        month = int(match2.group('month'))
        if match2.group('year'):
            year = int(match2.group('year'))
            # 年数が下２桁のみの場合は補完する
            if len(match2.group('year')) == 2:
                tmp_year = year + date.year // 100 * 100
                tmp_date = datetime.date(tmp_year, month, day)
                year = tmp_year + (0 if tmp_date >= date else 100)

        # 年数が無い場合は、次に(month/day)の日付が来る年数を使用する
        else:
            tmp_date = datetime.date(date.year, month, day)
            year = date.year + (0 if tmp_date >= date else 1)

        return datetime.date(year, month, day).toordinal()

    @staticmethod
    def timetable(date, string, time_reg, times_delim):
        """タスクラインのパース結果から作業時間を取得する
        """
        # 当日の年月日を取得する
        year, month, day = date.year, date.month, date.day

        # 作業時間表現をリスト化する
        phrases = [t.strip(' ') for t in string.split(times_delim)]

        # 作業時間正規表現にマッチングさせる
        matchs = [time_reg.match(p) for p in phrases if p]
        if not all(matchs): raise ValueError()
        groupdicts = [m.groupdict() for m in matchs]

        # 年月日とマッチング結果からタイムスタンプを作成する
        dt = lambda h,m,s:int(datetime.datetime(
            year,month,day,int(h),int(m),int(s)).timestamp())
        get = lambda d,a,b,c:(d.get(a,0),d.get(b,0),d.get(c,0))
        table = [(dt(*get(d, 'shour', 'smin', 'ssec')),
            dt(*get(d, 'ehour', 'emin', 'esec'))) for d in groupdicts]

        return [(s, e-s) for s,e in table]

    #==========================================================================
    # タスクトリ → ジャーナル変換メソッド
    #==========================================================================
    @staticmethod
    def journal(date, tasktory, memo,
            journal_tmpl, taskline_tmpl, time_tmpl, times_delim, infinite):
        """タスクトリからジャーナル用テキストを作成する
        """
        # タスクライン初期化
        tasklines = {OPEN: '', WAIT: '', CLOSE: '', CONST: ''}

        # ジャーナルに表示するタスクトリの条件（優先度順）
        # ・当日の作業時間が計上されているものは表示する
        # ・ステータスがOPENで残り日数がinfiniteより大きいものは表示しない
        # ・ステータスがCLOSEのものは表示しない
        # ・上記以外のものは表示する
        for node in tasktory:
            if Journal.at_date(date, node):
                pass
            elif node.status == OPEN and\
                    node.deadline - date.toordinal() > infinite:
                continue
            elif node.status == CLOSE:
                continue
            else:
                pass

            # タスクライン
            tasklines[node.status] += Journal.taskline(
                    date, node, taskline_tmpl, time_tmpl,
                    times_delim, infinite) + '\n'
            # コメント
            if node.comments: tasklines[node.status] += '\n'.join(
                    [' # ' + c for c in node.comments.split('\n')]) + '\n'

        # ジャーナル作成
        journal = journal_tmpl.substitute({
            'YEAR': '{:04}'.format(date.year),
            'MONTH': '{:02}'.format(date.month),
            'DAY': '{:02}'.format(date.day),
            'OPENTASKS': tasklines[OPEN],
            'WAITTASKS': tasklines[WAIT],
            'CLOSETASKS': tasklines[CLOSE],
            'CONSTTASKS': tasklines[CONST],
            'MEMO': '' if memo is None else memo})

        return journal

    @staticmethod
    def at_date(date, node):
        """指定した日付の作業時間が計上されているかどうかを返す"""
        start = datetime.datetime.combine(date, datetime.time())
        end = start + datetime.timedelta(1)
        start = int(start.timestamp())
        end = int(end.timestamp())
        return any([start <= s < end for s,_ in node.timetable])

    @staticmethod
    def taskline(date, node, taskline_tmpl, time_tmpl, times_delim, infinite):
        """タスクラインを取得する
        """
        # 期日
        rest_days = node.deadline - date.toordinal()

        # 作業時間
        times_phrase = times_delim.join([
            Journal.time_phrase(s,t,time_tmpl)
            for s,t in node.timetable if s >= time.mktime(date.timetuple())])

        return taskline_tmpl.substitute({
            'PATH': node.path(),
            'DEADLINE': rest_days if rest_days <= infinite else 'inf',
            'TIMES': times_phrase})

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
            'SHOUR': start.hour, 'SMIN': form(start.minute),
            'SSEC': form(start.second), 'EHOUR': end.hour,
            'EMIN': form(end.minute), 'ESEC': form(end.second)})
