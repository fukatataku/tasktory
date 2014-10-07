#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

import os, datetime, time, configparser
from multiprocessing import Process, Pipe

import win32api

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager
from lib.ui.Journal import Journal
from lib.ui.TrayIcon import TrayIcon
from lib.monitor.monitor import file_monitor, dir_monitor
from lib.common.RWTemplate import RWTemplate

from lib.common.common import *
from lib.common.exceptions import *

def read_journal(journal_file):
    """ジャーナルを読み込んでタスクトリツリーを取得する
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
    try: memo = read_journal(journal_file)[1]\
            if os.path.isfile(journal_file) else ''
    except:
        # TODO
        return

    # 新しいジャーナルを書き出す
    write_journal(today, tree, memo, infinite, journal_file)

    #====================
    # 準備
    #====================
    # 新しいジャーナルを読み込む
    try: jtasks = read_journal(journal_file)[0]
    except:
        # TODO
        return

    # タスクトリのパスリスト
    paths = taskpaths(root, profile_name)

    # トレイアイコンを作成する
    conn1, conn2 = Pipe()
    tip = Process(target=TrayIcon,
            args=(conn2, ICON_PATH, POPMSG_MAP, repo_map))
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
    ownid = os.getpid()

    #====================
    # ループ
    #====================
    try:
        ignore = False
        while True:
            # 通知が来るまでブロック
            ret = conn1.recv()

            # 自身による更新を無視する
            if ret[0] == ownid: ignore = True if ret[1] == 0 else False
            if ignore: continue

            if ret[0] == jmpid:
                #========================================
                # ジャーナルが更新された場合の処理
                #========================================
                # ジャーナルを読み込む
                try:
                    new_jtasks, memo = read_journal(journal_file)
                except JournalReadException:
                    # 読み込み失敗
                    win32api.SendMessage(
                            hwnd, TrayIcon.MSG_POPUP, ERROR_JNL_READ, None)
                    continue
                except JournalOverlapTimetableException:
                    # 作業時間に重複あり
                    win32api.SendMessage(
                            hwnd, TrayIcon.MSG_POPUP, ERROR_JNL_OVLP, None)
                    continue
                except JournalDuplicateTasktoryException:
                    # タスクトリに重複あり
                    win32api.SendMessage(
                            hwnd, TrayIcon.MSG_POPUP, ERROR_JNL_DUPL, None)
                    continue

                # タスクの状態に変化が無ければ無視する
                if sametree(jtasks, new_jtasks): continue

                # ジャーナルの内容をツリーにマージする
                jtasks = new_jtasks
                new_tree = tree + jtasks

                # ツリー中の未設定の期日を補完する
                for node in new_tree:
                    if node.deadline is None:
                        node.deadline = far(node)

                # 作業時間の重複を確認する（非必須）
                if Manager.overlap(new_tree):
                    win32api.SendMessage(
                            hwnd, TrayIcon.MSG_POPUP, ERROR_JNL_OVLP, None)
                    continue

                # ファイルシステムへの書き出し開始を通知する
                conn2.send((ownid, 0))
                win32api.SendMessage(
                        hwnd, TrayIcon.MSG_POPUP, INFO_FS_START, None)

                # ファイルシステムに書き出す
                tree = new_tree
                for node in tree:
                    Manager.put(root, node, profile_name)

                # ファイルシステムへの書き出し完了を通知する
                win32api.SendMessage(
                        hwnd, TrayIcon.MSG_POPUP, INFO_FS_END, None)
                conn2.send((ownid, 1))

            elif ret[0] == tmpid:
                #========================================
                # ファイルシステムが更新された場合の処理
                #========================================
                # 現在のファイルシステムの状態を読み込む
                new_paths = taskpaths(root, profile_name)

                # 前回と比べて変化が無ければ無視する
                if paths == new_paths: continue

                # ジャーナルへの書き出し開始を通知する
                conn2.send((ownid, 0))
                win32api.SendMessage(
                        hwnd, TrayIcon.MSG_POPUP, INFO_JNL_START, None)

                # ファイルシステムからツリーを読み出してジャーナルに書き出す
                paths = new_paths
                tree = Manager.get_tree(root, profile_name)
                write_journal(today, tree, memo, infinite, journal_file)

                # ジャーナルへの書き出し完了を通知する
                win32api.SendMessage(
                        hwnd, TrayIcon.MSG_POPUP, INFO_JNL_END, None)
                conn2.send((ownid, 1))

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
