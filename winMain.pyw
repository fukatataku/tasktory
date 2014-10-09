#!C:/python/python3.4/pythonw
# -*- encoding:utf-8 -*-

import os, datetime, time, configparser
from multiprocessing import Process, Pipe

import win32api

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager
from lib.ui.Journal import Journal
from lib.ui.Report import Report
from lib.ui.TrayIcon import TrayIcon
from lib.monitor.monitor import file_monitor, dir_monitor
from lib.common.RWTemplate import RWTemplate

from lib.common.common import *
from lib.common.exceptions import *

BLOCK = 0
UNBLOCK = 1

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

def write_report(date, tree, repo_name, repo_func, repo_dir, repo_name_tmpl):
    # レポートテキストを作成する
    repo_text = repo_func(date, tree)

    # レポートファイルパスを作成する
    repo_filename = repo_name_tmpl.substitute({
        'YEAR' : str(date.year),
        'MONTH' : str(date.month),
        'DAY' : str(date.day),
        })
    repo_file = os.path.join(repo_dir, repo_name, repo_filename)

    # ディレクトリが無ければ作成する
    if not os.path.isdir(os.path.join(repo_dir, repo_name)):
        os.makedirs(os.path.join(repo_dir, repo_name))

    # ファイルに書き出す
    with open(repo_file, 'w') as f:
        f.write(repo_text)
    return

def initialize(date, root, profile_name, journal_file):
    """タスクトリシステムを初期化する
    """
    # ルートが存在しなければ、作成する
    if not os.path.isfile(os.path.join(root, profile_name)):
        Manager.put(root, Tasktory('', date.toordinal() + 3650), profile_name)

    # ジャーナルディレクトリが存在しなければ、作成する
    journal_dir = os.path.dirname(journal_file)
    if not os.path.isdir(journal_dir): os.makedirs(journal_dir)

    return

def prepare(date, root, profile_name, journal_file, infinite):
    """ループに入る前の準備
    """
    # ジャーナルが存在するなら、memoを取り出す
    memo = read_journal(journal_file)[1]\
            if os.path.isfile(journal_file) else ''

    # ファイルシステムからツリーを読み込む
    tree = Manager.get_tree(root, profile_name)

    # 新しいジャーナルを書き出す
    write_journal(date, tree, memo, infinite, journal_file)

    # 新しいジャーナルを読み込む
    jtree, memo = read_journal(journal_file)

    # ファイルシステムの状態を読み込む
    paths = Manager.listtask(root, profile_name)

    return jtree, paths, memo

def prepare_process(root, journal_file, commands):
    # トレイアイコン
    conn1, conn2 = Pipe()
    tray_icon = Process(target=TrayIcon,
            args=(conn2, ICON_PATH, POPMSG_MAP, commands))
    tray_icon.start()
    hwnd = conn1.recv()[1]

    # 監視プロセス
    jnl_monitor = Process(target=file_monitor, args=(journal_file, conn2))
    fs_monitor = Process(target=dir_monitor, args=(root, conn2))

    # プロセス開始
    jnl_monitor.start()
    fs_monitor.start()

    return tray_icon, jnl_monitor, fs_monitor, hwnd, conn1, conn2

def journal_updated(org_jtree, date, root, profile_name, journal_file, hwnd):
    # ジャーナルを読み込む
    new_jtree, memo = read_journal(journal_file)

    # タスクの状態に変化が無ければ無視する
    if Manager.same_tree(org_jtree, new_jtree):
        return org_jtree, memo

    # ファイルシステムからツリーを読み出す
    tree = Manager.get_tree(root, profile_name)

    # 読み出したツリーの内、更新対象タスクの当日の作業時間を抹消する
    start = datetime.datetime.combine(date, datetime.time())
    end = start + datetime.timedelta(1)
    start = int(start.timestamp())
    end = int(end.timestamp())
    for node in [tree.find(n.path()) for n in new_jtree]:
        if node is None: continue
        node.timetable = [t for t in node.timetable\
                if not (start <= t[0] < end)]

    # マージする
    new_tree = tree + new_jtree

    # 作業時間の重複の有無を確認する（非必須）
    if Manager.overlap(new_tree):
        pass

    # 未設定期日を補完する
    for node in new_tree:
        if node.deadline is None:
            node.deadline = max([n.deadline for n in node
                if n.deadline is not None])

    # ファイルシステムへの書き出し開始を通知する
    message(hwnd, INFO_FS_START)

    # ファイルシステムに書き出す
    for node in new_tree: Manager.put(root, node, profile_name)

    # ファイルシステムへの書き出し完了を通知する
    message(hwnd, INFO_FS_END)

    return new_jtree, memo

def filesystem_updated(org_paths, date, root, profile_name, journal_file,
        memo, infinite, hwnd):
    # 現在のファイルシステムの状態を読み込む
    new_paths = Manager.listtask(root, profile_name)

    # ファイルシステムの状態に変化が無ければ無視する
    if org_paths == new_paths:
        return org_paths

    # ファイルシステムからツリーを読み込む
    tree = Manager.get_tree(root, profile_name)

    # ジャーナルへの書き出し開始を通知する
    message(hwnd, INFO_JNL_START)

    # ジャーナルに書き出す
    write_journal(date, tree, memo, infinite, journal_file)

    # ジャーナルへの書き出し完了を通知する
    message(hwnd, INFO_JNL_END)

    return new_paths

def trayicon_command(par, date, root, profile_name,
        repo_map, repo_dir, repo_name_tmpl, hwnd):
    # レポート書き出し開始を通知する
    message(hwnd, INFO_REPO_START)

    # ファイルシステムからタスクツリーを読み込む
    tree = Manager.get_tree(root, profile_name)

    if par == 0:
        # 全てのレポートを出力する
        for k,v in repo_map.items():
            write_report(date, tree, v[0], v[1], repo_dir, repo_name_tmpl)
    else:
        # 指定されたレポートを出力する
        repo_name = repo_map[par][0]
        repo_func = repo_map[par][1]
        write_report(date, tree,
                repo_name, repo_func, repo_dir, repo_name_tmpl)

    # レポート書き出し完了を通知する
    message(hwnd, INFO_REPO_END)
    return

def message(hwnd, msg):
    """ポップアップメッセージを出力する
    """
    win32api.SendMessage(hwnd, TrayIcon.MSG_POPUP, msg, None)
    return

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
    report_dir = config['REPORT']['REPORT_DIR']
    report_name_tmpl = RWTemplate(config['REPORT']['REPORT_NAME'])

    #===================================
    # TODO: トレイアイコンコマンド
    #===================================
    com_map = {}
    commands = []
    def gen():
        n = 0
        while True:
            yield n
            n += 1
        return

    # 同期コマンド
    Id = gen()
    com_map[Id] = sync
    com_menu.append('Sync', Id))

    # レポートコマンド

    # セパレータ
    com_menu.append((None, None))

    # 終了コマンド
    Id = gen()
    com_map[Id] = quit
    com_menu.append('Quit', Id)

    com_map = {
            0 : sync, args,
            1 : report,
            2 : report,
            3 : report,
            4 : quit,
            }
    commands = [
            ('Sync', 0),
            ('Report', [
                ('ALL', 1),
                ('チーム週報', 2),
                ('チーム月報', 3),
                ]),
            (None, None),
            ('Quit', 4),
            ]

    # 日付
    today = datetime.date.today()

    #====================
    # 初期化
    #====================
    initialize(today, root, profile_name, journal_file)

    #====================
    # 準備
    #====================
    jtree, paths, memo = prepare(
            today, root, profile_name, journal_file, infinite)

    #====================
    # サブプロセス
    #====================
    tray_icon, jnl_monitor, fs_monitor, hwnd, conn1, conn2 = prepare_process(
            root, journal_file, commands)
    ownid = os.getpid()

    #====================
    # ループ
    #====================
    try:
        ignore = UNBLOCK
        while True:
            # 通知が来るまでブロック
            ret = conn1.recv()

            # 自身による更新を無視する
            if ret[0] == ownid:
                ignore = ret[1]
                continue
            if ignore == BLOCK:
                continue

            if ret[0] == jnl_monitor.pid:
                #========================================
                # ジャーナルが更新された場合の処理
                #========================================
                conn2.send((ownid, BLOCK))
                try:
                    jtree, memo = journal_updated(
                            jtree, today, root, profile_name, journal_file,
                            hwnd)
                except JournalReadException:
                    # 読み込み失敗
                    message(hwnd, ERROR_JNL_READ)
                    continue
                except JournalOverlapTimetableException:
                    # 作業時間に重複あり
                    message(hwnd, ERROR_JNL_OVLP)
                    continue
                except JournalDuplicateTasktoryException:
                    # タスクトリに重複あり
                    message(hwnd, ERROR_JNL_DUPL)
                    continue
                finally:
                    conn2.send((ownid, UNBLOCK))

            elif ret[0] == fs_monitor.pid:
                #========================================
                # ファイルシステムが更新された場合の処理
                #========================================
                conn2.send((ownid, BLOCK))
                try:
                    paths = filesystem_updated(
                            paths, today, root, profile_name, journal_file,
                            memo, infinite, hwnd)
                finally:
                    conn2.send((ownid, UNBLOCK))

            elif ret[0] == tray_icon.pid:
                #========================================
                # コマンドが実行された場合の処理
                #========================================
                # 終了コマンド
                if ret[1] == 1024: break

                # 他のコマンド
                try:
                    trayicon_command(ret[1], today, root, profile_name,
                            repo_map, report_dir, report_name_tmpl, hwnd)
                except:
                    message(hwnd, ERROR_REPO_WRITE)

    finally:
        jnl_monitor.terminate()
        fs_monitor.terminate()
        conn1.close()
        conn2.close()

    return

if __name__ == '__main__':
    main()
