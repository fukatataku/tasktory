# -*- encoding:utf-8 -*-

from lib.common.RWTemplate import RWTemplate

SPAN = 7    # 過去７日分のレポートを出力する

TMPL_TEXT = """%YEAR/%MONTH/%DAY
◆Todo
%OPENTASKS
◆Wait
%WAITTASKS
◆Done
%CLOSETASKS
◆Const
%CONSTTASKS
◆Memo
%MEMO"""

ReportTemplate = RWTemplate(TMPL_TEXT)
TasklineTemplate = RWTemplate('%INDENT・%PATH (%ACHIVE_RATE)')

@staticmethod
def report(tasktory):
    return
