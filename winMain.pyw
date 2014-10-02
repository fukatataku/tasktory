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

def init():
    return

def sync():
    """ジャーナルの変更をファイルシステムに反映する
    """
    return

def main():
    # コンフィグを読み出す
    configparser.ConfigParser()
    config.read(MAIN_CONF_FILE)
    root = config['MAIN']['ROOT']
    profile_name = config['MAIN']['PROFILE_NAME']
    journal_file = config['JOURNAL']['JOURNAL_FILE']
    infinite = int(config['JOURNAL']['INFINITE'])

    # 初期化する

    # ファイルシステムからタスクツリーを読み出す
    tree = Manager.get_tree(root, profile_name)

    # 同期

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
                pass

            else ret == 1:
                # ファイルシステムが更新された場合の処理
                pass
            pass

    finally:
        jmp.terminate()
        tmp.terminate()

    return

if __name__ == '__main__':
    pass
