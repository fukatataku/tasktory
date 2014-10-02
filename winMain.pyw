#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

import sys, os, datetime, time, configparser
from multiprocessing import Process, Pipe

from lib.core.Manager import Manager
from lib.ui.Journal import Journal
from lib.monitor.monitor import file_monitor, dir_monitor

from lib.common.common import MAIN_CONF_FILE
from lib.common.common import JOURNAL_CONF_FILE
from lib.common.common import JOURNAL_READ_TMPL_FILE
from lib.common.common import JOURNAL_WRITE_TMPL_FILE

def sync():
    """ジャーナルの変更をファイルシステムに反映する
    """
    return

def put_journal(date, ):
    """タスクトリツリーをジャーナルに書き出す
    """
    # ジャーナル書き出し用のコンフィグを読み込む
    with open(JOURNAL_WRITE_TMPL_FILE, 'r') as f: journal_tmpl = f.read()
    config = configparser.ConfigParser()
    section = config['WriteTemplate']
    taskline_tmpl = RWTemplate(section['TASKLINE'])
    date_tmpl = RWTemplate(section['DATE'])
    time_tmpl = RWTemplate(section['TIME'])
    times_delim = section['TIMES_DELIM']

    # ツリーからジャーナルテキストを作成する
    journal = Journal.journal(date, tree, memo,
            journal_tmpl, taskline_tmpl, time_tmpl, times_delim, infinite)

    # ジャーナルテキストをファイルに書き出す
    with open(journal_file, 'w') as f:
        f.write(journal)

    # ジャーナル書き出し設定を読み込み設定にセットする
    with open(JOURNAL_READ_TMPL_FILE, 'w') as f: f.write(journal_tmpl)
    section = config['ReadTemplate']
    section['TASKLINE'] = taskline_tmpl.template
    section['DATE'] = date_tmpl.template
    section['TIME'] = time_tmpl.template
    section['TIMES_DELIM'] = times_delim
    with open(JOURNAL_CONF_FILE, 'w') as f: config.write(f)

    return

def main():
    # コンフィグを読み込む
    configparser.ConfigParser()
    config.read(MAIN_CONF_FILE)
    root = config['MAIN']['ROOT']
    profile_name = config['MAIN']['PROFILE_NAME']
    journal_file = config['JOURNAL']['JOURNAL_FILE']
    infinite = int(config['JOURNAL']['INFINITE'])

    # 日付
    today = datetime.date.today()

    # ルートが存在しなければ作成する
    if not os.path.isfile(os.path.join(root, profile_name)):
        Manager.put(root, Tasktory('', 3650))

    # ファイルシステムからタスクツリーを読み出す
    tree = Manager.get_tree(root, profile_name)

    # ジャーナルがあれば読んでおく
    # 無ければ作成する

    # 監視プロセスを作成する
    conn1, conn2 = Pipe()
    jmp = Process(target=file_monitor, args=(journal_file, conn2, 0))
    tmp = Process(target=dir_monitor, args=(root, conn2, 1))

    # 監視を開始する
    jmp.start()
    tmp.start()

    # ループ
    try:
        while True:
            # 通知が来るまでブロック
            ret = conn1.recv()

            if ret == 0:
                # ジャーナルが更新された場合の処理
                # 前回のジャーナルの内容と比較して、同期が必要かどうか確認する
                pass

            else ret == 1:
                # ファイルシステムが更新された場合の処理
                # 前回のファイルシステムの内容と比較
                pass
            pass

    finally:
        jmp.terminate()
        tmp.terminate()

    return

if __name__ == '__main__':
    pass
