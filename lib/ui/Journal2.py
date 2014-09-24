# -*- encoding:utf-8 -*-

import os, datetime, time

from lib.core.Tasktory import Tasktory

# 定数
OPEN = Tasktory.OPEN
WAIT = Tasktory.WAIT
CLOSE = Tasktory.CLOSE
CONST = Tasktory.CONST

class Journal:

    num_reg = re.compile(r'\d+$')
    head_reg = re.compile(r'^(%{?YEAR}?[^a-zA-Z0-9_%{}]+)')
    tail_reg = re.compile(r'([^a-zA-Z0-9_%{}]+%{?YEAR}?)$')
    delim_reg = re.compile(r'([^a-zA-Z0-9_%{}]+)')

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
    def tasktories(journal, journal_tmpl):
        """ジャーナルテキストを読み込んでパスとタスクトリのペアのリストを返す
        メモがあればそれも返す
        """
        # ジャーナルをパースする
        journal_dict = journal_tmpl.parse(journal)

        # ジャーナルの日付
        datestamp = datetime.date(
                int(journal_dict['YEAR']),
                int(journal_dict['MONTH']),
                int(journal_dict['DAY'])).toordinal()

        # タスクライン
        tasklines = {}
        split = lambda obj:[o for o in obj.split('\n') if o.strip(' ') != '']
        for k1, k2 in zip((OPEN, WAIT, CLOSE, CONST),
                ('OPENTASKS', 'WAITTASKS', 'CLOSETASKS', 'CONSTTASKS')):
            tasklines[k1] = split(journal_dict[k2])

        # 各タスクラインをタスクトリに変換する
        tasks = {}
        conv = lambda t,s:Journal.tasktory(t, config, datestamp, s)
        for key in (OPEN, WAIT, CLOSE, CONST):
            tasks[key] = [conv(t, key) for t in tasklines[key]]

        # メモ
        memo = journal_obj['MEMO']

        # 各タスクリストを結合して返す
        return sum(tasks.values(), []), memo

    @staticmethod
    def tasktory(date, status, taskline,
            taskline_tmpl, date_reg, time_reg, times_delim):
        """タスクラインからタスクトリを生成し、親タスクトリまでのパスと生成した
        タスクトリを返す
        date : ジャーナルの日付（datetime.dateオブジェクト）
        status : タスクラインのステータス
        taskline : ジャーナルテキストから読み出したタスクライン
        """
        # タスクラインをテンプレートに従ってパースする
        taskdict = taskline_tmpl.parse(taskline)

        # タスクトリ名を解決する
        name = os.path.basename(taskdict['PATH'])

        # 期日を解決する
        deadline = Journal.deadline(date, taskdict['DEADLINE'], date_reg)

        # タスクトリを作成する
        task = Tasktory(name, deadline, status)

        # 作業時間を解決する
        [task.add_time(s,t) for s,t in Journal.timetable(
            date, taskdict['TIMES'], time_reg, times_delim)]

        return os.path.dirname(taskdict['PATH']), task

    @staticmethod
    def deadline(date, string, date_reg):
        """タスクラインパース結果から期日を取得する
        """
        datestamp = date.toordinal()

        # 数値が１つだけの場合は残り日数として解釈する
        match1 = Journal.num_reg.match(string)
        if match1: return datestamp + int(match1.group())

        match2 = date_reg.match(string)
        if not match2: raise ValueError()

        # 数値が２つ以上の場合は日付として解釈する
        day = int(match2.group('day'))
        month = int(match2.group('month'))
        if match2.group('year'):
            year = int(match2.group('year'))

        # 年数が無い場合は、次に(month/day)の日付が来る年数を使用する
        else:
            tmp_datestamp = datetime.date(date.year, month, day).toordinal()
            year = date.year + (0 if tmp_datestamp >= datestamp else 1)

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

        # マッチング結果から各時間要素を取り出す
        gets = tuple(lambda d:d.get(s, 0)
                for s in ('shour', 'smin', 'ssec', 'ehour', 'emin', 'esec'))
        times = [tuple(get(d) for get in gets) for d in groupdicts]

        # 年月日と時間要素からタイムスタンプを作成、タイムテーブルに変換する
        dt = lambda h,m,s:datetime.datetime(year,month,day,h,m,s).timestamp()
        table = [(dt(sh,sm,ss), dt(eh,em,es)) for sh,sm,ss,eh,em,es in times]

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

        for node in tasktory:
            if (node.status == CLOSE or\
                    node.deadline - date.toordinal() > infinite): continue
            tasklines[node.status] += Journal.taskline(
                    date, node, taskline_tmpl, time_tmpl, times_delim) + '\n'

        # ジャーナル作成
        journal = journal_tmpl.substitute({
            'YEAR': date.year, 'MONTH': date.month, 'DAY': date.day,
            'OPENTASKS': tasklines[OPEN],
            'WAITTASKS': tasklines[WAIT],
            'CLOSETASKS': tasklines[CLOSE],
            'CONSTTASKS': tasklines[CONST],
            'MEMO': '' if memo is None else memo})

        return journal

    @staticmethod
    def taskline(date, node, taskline_tmpl, time_tmpl, times_delim):
        """タスクラインを取得する
        """
        # 作業時間
        times_phrase = times_delim.join([
            Journal.time_phrase(s,t,time_tmpl)
            for s,t in node.timetable if s >= time.mktime(date.timetuple())])

        return taskline_tmpl.substitute({
            'PATH': node.get_path(),
            'DEADLINE': node.deadline - date.toordinal(),
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
