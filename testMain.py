#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

import datetime

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager

from jinja2 import Environment, FileSystemLoader

TMPL_DIR = "C:/home/fukata/dev/tasktory/template"
TMPL_NAME = "summary.tmpl"
OUTPUT = "C:/home/fukata/tmp/summary.html"

INF = 365 * 100

if __name__ == '__main__':
    #==========================================================================
    # タスクトリ作成
    #==========================================================================
    today = datetime.date.today()
    today_ord = today.toordinal()
    today_ts = datetime.datetime.combine(today, datetime.time())

    root = Tasktory('', today_ord + INF*2)
    proj1 = Tasktory('Project1', today_ord + INF*2); root.append(proj1)
    proj2 = Tasktory('Project2', today_ord + INF*2); root.append(proj2)

    taskA = Tasktory('TaskA', today_ord + 10); proj1.append(taskA)
    step1 = Tasktory('step1', today_ord + 0); taskA.append(step1)
    step2 = Tasktory('step2', today_ord + 5); taskA.append(step2)
    step3 = Tasktory('step3', today_ord + 7); taskA.append(step3)
    step4 = Tasktory('step4', today_ord + 10); taskA.append(step4)

    taskB = Tasktory('TaskB', today_ord + 20); proj1.append(taskB)
    step1 = Tasktory('step1', today_ord + 13); taskB.append(step1)
    step2 = Tasktory('step2', today_ord + 16); taskB.append(step2)
    step3 = Tasktory('step3', today_ord + 20); taskB.append(step3)

    step1.add_time(today_ts, 3600)

    #==========================================================================
    # テンプレート初期化
    #==========================================================================
    env = Environment(loader=FileSystemLoader(TMPL_DIR))
    tmpl = env.get_template(TMPL_NAME)

    #==========================================================================
    # レンダリング用の属性をツリーに追加する
    #==========================================================================
    for node in root:
        setattr(node, 'deadline_str' ,
                datetime.date.fromordinal(node.deadline).strftime('%Y/%m/%d'))
        setattr(node, 'rest_days' ,
                node.deadline - today_ord)

    #==========================================================================
    # テキストレンダリング
    #==========================================================================
    text = tmpl.render(tree=root)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(text)
    pass
