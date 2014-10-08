#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import datetime

# テスト用コード
import sys, os
THIS_DIR = os.path.dirname(__file__)
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..', '..'))
sys.path.append(HOME_DIR)
# テスト用コードここまで

from lib.core.Tasktory import Tasktory
from lib.common.RWTemplate import RWTemplate

#=======================================
# 設定値
#=======================================
SPAN = 7        # 過去７日分のレポートを出力する
INFINITE = 365  # 期日が365日より先のものは出力しない
INDENT = '  '   # インデントに使用する文字列

# テンプレート
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

#=======================================
# レポート名
#=======================================
# 以下の変数名は変更禁止
REPORT_NAME = 'サンプル'

#=======================================
# レポート出力
#=======================================
# 以下の関数名、引数は変更禁止
def report(date, tasktory):
    """タスクトリを受け取ってレポートテキストを返す
    date : レポートの日付を示すdatetime.dateオブジェクト
    tasktory : タスクトリオブジェクト
    """
    # 日付
    sdate = date - datetime.timedelta(SPAN-1)

    # 今週の作業
    start = datetime.datetime(
            sdate.year, sdate.month, sdate.day, 0, 0, 0).timestamp()
    end = (datetime.datetime(date.year, date.month, date.day, 0, 0, 0) +\
            datetime.timedelta(1)).timestamp()

    thisweek = ''
    clip = tasktory.clip(lambda t:at(t, start, end))
    for node in [] if clip is None else clip:
        # 出力条件
        # ・ルートタスクトリは表示しない
        # ・指定期間に作業時間が計上されている事（clipで解決済み）
        # ・期日が規定以上遠ければ進捗率を表示しない
        if node.level() == 0: continue
        org = tasktory.search(lambda t:t.ID == node.ID)[0]
        rest = node.deadline - date.toordinal()
        rate = achieve_rate(org)
        tmpl = TasklineTemplate if rest <= INFINITE else SimpleTasklineTemplate
        thisweek += tmpl.substitute({'INDENT': INDENT * (node.level()-1),
            'PATH': node.name, 'ACHIEVE_RATE': '{}'.format(rate)}) +'\n'
        if node.comments:
            thisweek += INDENT * (node.level()) + '# ' + node.comments + '\n'

    # 来週の作業
    # OPEN, WAITのタスクを出力する
    nextweek = ''
    clip = tasktory.clip(lambda t:t.status != Tasktory.CLOSE)
    for node in [] if clip is None else clip:
        if node.level() == 0: continue
        if node.deadline - date.toordinal() > INFINITE: continue
        nextweek += SimpleTasklineTemplate.substitute({
            'INDENT': INDENT * (node.level()-1), 'PATH': node.name}) +'\n'
        if node.comments:
            nextweek += INDENT * (node.level()) + '# ' + node.comments + '\n'

    # レポートテキストを作成して返す
    return ReportTemplate.substitute({
        'SMONTH': sdate.month, 'SDAY': sdate.day,
        'EMONTH': date.month, 'EDAY': date.day,
        'THISWEEK': thisweek, 'NEXTWEEK': nextweek})

#=======================================
# 補助関数
#=======================================
def at(node, start, end):
    """タスクトリが指定した期間に作業されていたかどうかを返す
    node : タスクトリ
    start : 条件期間の開始エポック秒
    end : 条件期間の終了エポック秒
    ※ 条件は start < t < end となる事に注意
    """
    for s,t in node.timetable:
        if s < end and (s+t) >= start: return True
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
    t0 = Tasktory('', today.toordinal()); t0.add_time(timestamp, 3600)
    t01 = Tasktory('ProjectA', today.toordinal()); t01.add_time(timestamp, 3600)
    t02 = Tasktory('ProjectB', today.toordinal()); t02.add_time(timestamp, 3600)
    t03 = Tasktory('ProjectC', today.toordinal()); t03.add_time(timestamp, 3600)
    t021 = Tasktory('Task1', today.toordinal()); t021.add_time(timestamp, 3600)
    t0211 = Tasktory('Step1', today.toordinal()); t0211.add_time(timestamp,3600)
    t0212 = Tasktory('Step2', today.toordinal()); t0212.add_time(timestamp,3600)
    t0212.comments = 'Waiting Mr.Yamaguchi\'s answer'
    t0213 = Tasktory('Step3', today.toordinal()); t0213.add_time(timestamp,3600)
    t022 = Tasktory('Task2', today.toordinal()); t022.add_time(timestamp, 3600)
    t0.append(t01); t01.status = Tasktory.CLOSE
    t0.append(t02)
    t0.append(t03)
    t02.append(t021);
    t02.append(t022);
    t021.append(t0211); t0211.status = Tasktory.CLOSE
    t021.append(t0212);
    t021.append(t0213);

    text = report(today, t0)
    print(text)

    #test = lambda t:at(t,
            #datetime.datetime(2014, 9, 12).timestamp(),
            #datetime.datetime(2014, 10, 1).timestamp())
    #print(test(t0))

    #filepath = "C:/home/fukata/tmp/test.txt"
    #with open(filepath, 'w', encoding='utf-8') as f:
        #f.write(text)

