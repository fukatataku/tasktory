#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import datetime

# テスト用コード
import sys, os
THIS_DIR = os.path.dirname(__file__)
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..', '..'))
sys.path.append(HOME_DIR)

from lib.core.Tasktory import Tasktory
from lib.common.RWTemplate import RWTemplate

SPAN = 7    # 過去７日分のレポートを出力する
INFINITE = 365
INDENT = '  '

REPORT_TMPLSTR = """To: BOSS

Hi, I'm me.
I send you to work report between %SMONTH/%SDAY to %EMONTH/%EDAY

<This week work>
%THISWEEK
<Next week work>
%NEXTWEEK
Thanks.
"""
TASKLINE_TMPLSTR = "%INDENT* %PATH (%ACHIEVE_RATE%%)"
SIMPLE_TASKLINE_TMPLSTR = "%INDENT* %PATH"

ReportTemplate = RWTemplate(REPORT_TMPLSTR)
TasklineTemplate = RWTemplate(TASKLINE_TMPLSTR)
SimpleTasklineTemplate = RWTemplate(SIMPLE_TASKLINE_TMPLSTR)

def report(date, tasktory, *args, **kwargs):
    """タスクトリを受け取ってレポートテキストを返す
    date : レポートの日付を示すdatetime.dateオブジェクト
    tasktory : タスクトリオブジェクト
    args : 拡張用
    kwargs : 拡張用
    """
    # 日付
    sdate = date - datetime.timedelta(7)

    # 今週の作業
    start = datetime.datetime(
            sdate.year, sdate.month, sdate.day, 0, 0, 0).timestamp()
    end = (datetime.datetime(date.year, date.month, date.day, 0, 0, 0) +\
            datetime.timedelta(1)).timestamp()

    thisweek = ''
    for node in tasktory.clip(lambda t:at(t, start, end)):
        # 出力条件
        # ・指定期間に作業時間が計上されている事（clipで解決済み）
        # ・期日が規定以上遠ければ進捗率を表示しない
        org = tasktory[node.ID]
        rest = node.deadline - date.toordinal()
        rate = achieve_rate(org)
        tmpl = TasklineTemplate if rest <= INFINITE else SimpleTasklineTemplate
        thisweek += tmpl.substitute({'INDENT': INDENT * node.level(),
            'PATH': node.name, 'ACHIEVE_RATE': '{}'.format(rate)}) +'\n'

    # 来週の作業
    # OPEN, WAITのタスクを出力する
    nextweek = ''
    for node in tasktory.clip(lambda t:at(t, start, end) and\
            t.status != Tasktory.CLOSE):
        if node.deadline - date.toordinal() > INFINITE: continue
        nextweek += SimpleTasklineTemplate.substitute({
            'INDENT': INDENT * node.level(), 'PATH': node.name}) +'\n'

    # レポートテキストを作成して返す
    return ReportTemplate.substitute({
        'SMONTH': sdate.month, 'SDAY': sdate.day,
        'EMONTH': date.month, 'EDAY': date.day,
        'THISWEEK': thisweek, 'NEXTWEEK': nextweek})

def at(node, start, end):
    """タスクトリが指定した期間に作業されていたかどうかを返す
    node : タスクトリ
    start : 条件期間の開始エポック秒
    end : 条件期間の終了エポック秒
    ※ 条件は start < t < end となる事に注意
    """
    for s,t in node.timetable:
        if s < end and (s+t) > start: return True
    return False

def achieve_rate(node):
    """タスクトリの進捗率を返す
    """
    if node.children:
        close_num = len([c for c in node.children if c.status==Tasktory.CLOSE])
        rate = int((close_num / len(node.children)) * 100)
    else:
        rate = 100 if node.status == Tasktory.CLOSE else 0
    return rate

if __name__ == '__main__':
    today = datetime.date.today()
    timestamp = datetime.datetime(today.year, today.month, today.day
            , 0, 0, 0).timestamp()
    t0 = Tasktory(1, 'HOGE', today.toordinal()); t0.add_time(timestamp, 3600)
    t1 = Tasktory(2, 'FUGA', today.toordinal()); t1.add_time(timestamp, 3600)
    t2 = Tasktory(3, 'PIYO', today.toordinal()); t2.add_time(timestamp, 3600)
    t4 = Tasktory(5, 'BBB', today.toordinal()); t4.add_time(timestamp, 3600)
    t5 = Tasktory(6, 'CCC', today.toordinal()); t5.add_time(timestamp, 3600)
    t6 = Tasktory(7, 'DDD', today.toordinal()); t6.add_time(timestamp, 3600)
    t0.append(t1); t1.status = Tasktory.CLOSE
    t0.append(t2)
    t0.append(t4)
    t2.append(t5); t5.status = Tasktory.CLOSE
    t2.append(t6); t6.status = Tasktory.CLOSE

    text = report(t0, today)
    print(text)

    #test = lambda t:at(t,
            #datetime.datetime(2014, 9, 12).timestamp(),
            #datetime.datetime(2014, 10, 1).timestamp())
    #print(test(t0))

    #filepath = "C:/home/fukata/tmp/test.txt"
    #with open(filepath, 'w', encoding='utf-8') as f:
        #f.write(text)

