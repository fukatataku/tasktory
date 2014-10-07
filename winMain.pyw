#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

import sys, os, datetime, time, configparser
from multiprocessing import Process, Pipe

import win32api

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager
from lib.ui.Journal import Journal
from lib.ui.TrayIcon import TrayIcon
from lib.monitor.monitor import file_monitor, dir_monitor
from lib.common.RWTemplate import RWTemplate

from lib.common.common import MAIN_CONF_FILE
from lib.common.common import JOURNAL_CONF_FILE
from lib.common.common import JOURNAL_READ_TMPL_FILE
from lib.common.common import JOURNAL_WRITE_TMPL_FILE
from lib.common.common import ICON_PATH

from lib.common.exceptions import JournalReadException
from lib.common.exceptions import JournalOverlapTimetableException
from lib.common.exceptions import JournalDuplicateTasktoryException

def read_journal(journal_file):
    """ジャーナルを読みでタスクトリツリーを取得する
    """
    # ジャーナル読み込み用のコンフィグを読み込む
    with open(JOURNAL_READ_TMPL_FILE, 'r', encoding='utf-8-sig') as f:
        journal_tmpl = RWTemplate(f.read())
    config = configparser.ConfigParser()
    config.read(JOURNAL_CONF_FILE, encoding='utf-8-sig')
    section = config['ReadTemplate']
    taskline_tmpl = RWTemplate(section['TASKLINE'])
    date_reg = Journal.date_regex(section['DATE'])
    time_reg = Journal.time_regex(section['TIME'])
    times_delim = section['TIMES_DELIM']

    # ファイルからジャーナルテキストを読み込む
    with open(journal_file, 'r', encoding='utf-8-sig') as f:
        journal = f.read()

    # ジャーナルからタスクトリリストを作成する
    tasktories, memo = Journal.tasktories(journal,
            journal_tmpl, taskline_tmpl, date_reg, time_reg, times_delim)

    # 同じタスクトリが複数存在する場合は例外を送出する
    paths = [Journal.foot(t).path() for t in tasktories]
    if len(paths) != len(set(paths)):
        raise JournalDuplicateTasktoryException()

    # タスクトリリストをツリーに統合する
    tree = sum(tasktories[1:], tasktories[0]) if tasktories else None

    # ツリーを診断する
    if tree is not None and Manager.overlap(tree):
        raise JournalOverlapTimetableException()

    return tree, memo

def write_journal(date, tree, memo, infinite, journal_file):
    """タスクトリツリーをジャーナルに書き出す
    """
    # ジャーナル書き出し用のコンフィグを読み込む
    with open(JOURNAL_WRITE_TMPL_FILE, 'r', encoding='utf-8-sig') as f:
        journal_tmpl = RWTemplate(f.read())
    config = configparser.ConfigParser()
    config.read(JOURNAL_CONF_FILE, encoding='utf-8-sig')
    section = config['WriteTemplate']
    taskline_tmpl = RWTemplate(section['TASKLINE'])
    date_tmpl = RWTemplate(section['DATE'])
    time_tmpl = RWTemplate(section['TIME'])
    times_delim = section['TIMES_DELIM']

    # ツリーからジャーナルテキストを作成する
    journal = Journal.journal(date, tree, memo,
            journal_tmpl, taskline_tmpl, time_tmpl, times_delim, infinite)

    # ジャーナルテキストをファイルに書き出す
    with open(journal_file, 'w', encoding='utf-8') as f:
        f.write(journal)

    # ジャーナル書き出し設定を読み込み設定にセットする
    with open(JOURNAL_READ_TMPL_FILE, 'w', encoding='utf-8') as f:
        f.write(journal_tmpl.template)
    section = config['ReadTemplate']
    section['TASKLINE'] = taskline_tmpl.template.replace('%', '%%')
    section['DATE'] = date_tmpl.template.replace('%', '%%')
    section['TIME'] = time_tmpl.template.replace('%', '%%')
    section['TIMES_DELIM'] = times_delim
    with open(JOURNAL_CONF_FILE, 'w', encoding='utf-8') as f:
        config.write(f)

    return

def same(task1, task2):
    """２つのタスクトリ間に差分があるかどうかを調べる。
    差分があればFalse、無ければTrueを返す。
    差分として認める差異は
    ・タイムテーブルの差異
    ・ステータスの差異
    ・期日の差異
    """
    # 名前をチェックする
    if task1.name != task2.name:
        raise ValueError()

    # 作業時間の差異をチェックする
    if set(task1.timetable) != set(task2.timetable):
        return False

    # ステータスの差異をチェックする
    if task1.status != task2.status:
        return False

    # 期日の差異をチェックする
    if task1.deadline != task2.deadline:
        return False

    return True

def sametree(tree1, tree2):
    """２つのタスクツリーの間に差分があるかどうかを調べる。
    差分があればFalse、無ければTrueを返す。
    差分として認める差異は
    ・タスクトリの有無
    ・タスクトリの作業時間の差異
    ・タスクトリのステータスの差異
    ・タスクトリの期日の差異
    """
    if tree1 is None and tree2 is None: return True
    if tree1 is None and tree2 is not None: return False
    if tree1 is not None and tree2 is None: return False
    for t1, t2 in zip(tree1, tree2):
        if t1.name != t2.name: return False
        if not same(t1, t2): return False
    return True

def taskpaths(dirpath, profile_name):
    """指定したディレクトリ以下に含まれるタスクトリのパスのリストを取得する
    """
    paths = [os.path.join(dirpath, p).replace('\\', '/')
            for p in os.listdir(dirpath)]
    dirs = [p for p in paths if os.path.isdir(p)]
    tasks = set([p for p in dirs
        if os.path.exists(os.path.join(p, profile_name))])
    return set.union(tasks, *[taskpaths(p, profile_name) for p in tasks])

def far(task):
    return max([far(t) for t in task.children] + [task.deadline],
            key=lambda x:-1 if x is None else x)

def main():
    #====================
    # 設定読み込み
    #====================
    config = configparser.ConfigParser()
    config.read(MAIN_CONF_FILE, encoding='utf-8-sig')
    root = config['MAIN']['ROOT']
    profile_name = config['MAIN']['PROFILE_NAME']
    journal_file = config['JOURNAL']['JOURNAL_FILE']
    infinite = int(config['JOURNAL']['INFINITE'])

    # TODO: ポップアップメッセージ
    popmsg_map = {
            0 : ('Journal Error', '作業時間の重複'),
            1 : ('Journal Error', '同名のタスクトリ'),
            2 : ('Journal Updated', 'ファイルシステムに書き出し開始'),
            3 : ('Journal Updated', 'ファイルシステムに書き出し完了'),
            4 : ('File System Updated', 'ジャーナルに書き出し開始'),
            5 : ('File System Updated', 'ジャーナルに書き出し完了'),
            6 : ('Journal Error', 'ジャーナル読み込み失敗')
            }

    #  TODO: レポート
    repo_map = {
            0 : 'all',
            1 : 'sample',
            }

    # 日付
    today = datetime.date.today()

    #====================
    # 初期化
    #====================
    # ルートが存在しなければ作成する
    if not os.path.isfile(os.path.join(root, profile_name)):
        Manager.put(root, Tasktory('', today.toordinal() + 3650), profile_name)

    # ジャーナルディレクトリが存在しなければ作成する
    journal_dir = os.path.dirname(journal_file)
    if not os.path.isdir(journal_dir): os.makedirs(journal_dir)

    # ファイルシステムからタスクツリーを読み出す
    tree = Manager.get_tree(root, profile_name)

    # ジャーナルからmemoを取得する
    # TODO: 例外処理
    memo = read_journal(journal_file)[1]\
            if os.path.isfile(journal_file) else ''

    # 新しいジャーナルを書き出す
    write_journal(today, tree, memo, infinite, journal_file)

    #====================
    # 準備
    #====================
    # 新しいジャーナルを読み込む
    # TODO: 例外処理
    tasks = read_journal(journal_file)[0]

    # タスクトリのパスリスト
    paths = taskpaths(root, profile_name)

    # トレイアイコンを作成する
    conn1, conn2 = Pipe()
    tip = Process(target=TrayIcon,
            args=(conn2, ICON_PATH, popmsg_map, repo_map))
    tip.start()
    hwnd = conn1.recv()[1]

    # 監視プロセスを作成する
    jmp = Process(target=file_monitor, args=(journal_file, conn2))
    tmp = Process(target=dir_monitor, args=(root, conn2))

    # 監視を開始する
    jmp.start()
    tmp.start()

    # プロセスIDを取得する
    tipid = tip.pid
    jmpid = jmp.pid
    tmpid = tmp.pid

    #====================
    # ループ
    #====================
    try:
        while True:
            # 通知が来るまでブロック
            ret = conn1.recv()

            if ret[0] == jmpid:
                #========================================
                # ジャーナルが更新された場合の処理
                #========================================
                try:
                    new_tasks, memo = read_journal(journal_file)
                except JournalReadException:
                    win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 6, None)
                    continue
                except JournalOverlapTimetableException:
                    win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 0, None)
                    continue
                except JournalDuplicateTasktoryException:
                    win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 1, None)
                    continue
                if sametree(tasks, new_tasks): continue

                # ジャーナルの内容をツリーにマージしてシステムに書き出す
                tasks = new_tasks
                new_tree = tree + tasks

                # 期日補正
                for node in new_tree:
                    if node.deadline is None:
                        node.deadline = far(node)
                if Manager.overlap(new_tree):
                    win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 0, None)
                    continue
                tree = new_tree

                # ファイルシステムへの書き出し開始を通知する
                win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 2, None)

                for node in tree:
                    Manager.put(root, node, profile_name)

                # ファイルシステムへの書き出し完了を通知する
                win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 3, None)

            elif ret[0] == tmpid:
                #========================================
                # ファイルシステムが更新された場合の処理
                #========================================
                new_paths = taskpaths(root, profile_name)
                if paths == new_paths: continue

                # ファイルシステムからツリーを読み出してジャーナルに書き出す
                paths = new_paths
                # ジャーナルへの書き出し開始を通知する
                win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 4, None)

                tree = Manager.get_tree(root, profile_name)
                write_journal(today, tree, memo, infinite, journal_file)

                # ジャーナルへの書き出し完了を通知する
                win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, 5, None)

            elif ret[0] == tipid:
                #========================================
                # トレイアイコンからコマンドが実行された場合の処理
                #========================================
                if ret[1] == 1024:
                    # 終了する
                    break
                pass

    finally:
        jmp.terminate()
        tmp.terminate()
        conn1.close()
        conn2.close()

    return

if __name__ == '__main__':
    main()
