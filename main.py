#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import sys, os, datetime, time, configparser

from lib.core.Manager import Manager
from lib.ui.Journal import Journal
from lib.common.common import JOURNAL_CONF_FILE

def main():
    # コンフィグ
    # ・タスクトリのルート
    # ・処理のスパン
    # ・ジャーナルのパス

    root = "C:/home/fukata/work"
    span = 10 # １０秒に１回
    journal_path = "C:/home/fukata/journal.txt"
    profile_name = '.profile'
    infinite = 365

    today = datetime.date.today()

    #======================
    # ループに入る前の準備
    #======================
    # コンフィグ
    config = configparser.ConfigParser()
    config.read(JOURNAL_CONF_FILE)
    journal_tmpl = config['READ_TEMPLATE']['JOURNAL_TMPL']

    # ジャーナルを有れば読み出す
    if os.path.isfile(journal_path):
        with open(journal_path, 'r') as f:
            journal = f.read()
        tasktories, memo = Journal.tasktories(journal, journal_tmpl)

    # ファイルシステムからタスクツリーを読み出す
    tree = Manager.get_tree(root, profile_name)

    # ジャーナルを書き出す
    journal = Journal.journal(today, tree, memo, journal_tmpl,
            taskline_tmpl, time_tmpl, times_delim, infinite)
    with open(journal_path, 'w') as f:
        f.write(journal)

def sync():
    """ジャーナルを読んでファイルシステムにコミットする
    """
    return

if __name__ == '__main__':
    # 処理内容
    # ・常駐する
    # ・定期的に以下の処理を行う
    #   ・ファイルシステムからタスクトリツリーを読み込む
    #   ・ジャーナルに更新があれば、コミットする
    #   ・レポートを書き出す
    # ・終了処理は確実にする
    #   どんなタイミングで終了シグナルが送られても適切に終了する

    # とりあえず、常駐スクリプトを書いてみる
    # ウィンドウが表示されないようにする
    # pywin32を使えば常駐スクリプト(サービス)は簡単に作れる
    # しかしドキュメントが少なく、特定のファイルの更新に関するイベントが不明
    # とりあえずポーリングでやる

    main()

    pass
