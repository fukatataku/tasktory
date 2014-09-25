#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import sys, os, datetime, time, configparser

from lib.core.Manager import Manager
from lib.ui.Journal import Journal
from lib.common.common import MAIN_CONF_FILE
from lib.common.common import JOURNAL_CONF_FILE
from lib.common.common import JOURNAL_READ_TMPL_FILE
from lib.common.common import JOURNAL_WRITE_TMPL_FILE

def main():
    # コンフィグを読み出す
    configparser.ConfigParser()
    config.read(MAIN_CONF_FILE)
    section = config['MAIN']
    root = section['ROOT']
    profile_name = section['PROFILE']
    journal_file = section['JOURNAL']
    infinite = int(section['INFINITE'])

    # ファイルシステムからタスクツリーを読み出す
    tree = Manager.get_tree(root, profile_name)

    # ループに入る
    timestamp = 0
    while True:
        # ジャーナルのタイムスタンプを確認する
        ts = os.stat(journal_file).st_mtime
        if timestamp == ts:
            time.sleep(30)
            continue
        timestamp = ts

        # 日付を取得する
        today = datetime.date.today()

        # 同期する
        try:
            new_tree = sync(today, root, tree,
                    journal_file, profile_name, infinite)
            tree = new_tree
        except ValueError():
            # TODO: エラー出力
            pass

        # 一定時間待機
        time.sleep(30)
    return

def sync(date, root, tree, journal_file,
        profile_name, infinite):
    """タスクトリ、ジャーナル、ファイルシステムを同期する
    tree : 予めファイルシステムから読み出したタスクツリー
    date : 書き出すジャーナルの日付を表すdatetime.dateオブジェクト
    root : ルートタスクトリのパス
    profile_name : タスクトリプロファイルのファイル名
    journal_file : ジャーナルファイルのパス
    infinite : 無期タスクの閾値
    """
    # ジャーナル読み出し用のコンフィグを読み込む
    with open(JOURNAL_READ_TMPL_FILE, 'r') as f:
        journal_tmpl = f.read()
    config = configparser.ConfigParser()
    config.read(JOURNAL_CONF_FILE)
    section = config['ReadTemplate']
    taskline_tmpl = section['TASKLINE']
    date_tmpl = section['DATE']
    date_reg = Journal.date_reg(date_tmpl)
    time_tmpl = section['TIME']
    time_reg = Journal.time_reg(time_tmpl)
    times_delim = section['TIMES_DELIM']

    # ジャーナルを読み出して、ジャーナルテキストを取得する
    with open(journal_file, 'r') as f:
        journal = f.read()

    # ジャーナルテキストからタスクトリリストを作成する
    tasktories, memo = Journal.tasktories(journal, journal_tmpl, taskline_tmpl,
            date_reg, time_reg, times_delim)

    # 作成したタスクトリをツリーにマージする
    new_tree = sum(tasktories, tree)

    # ツリーを診断する
    if Manager.overlap(new_tree):
        raise ValueError()

    # マージしたツリーをファイルシステムに書き出す
    for node in new_tree: Manager.put(root, node, profile_name)

    # ジャーナル書き込み用のコンフィグを読み込む
    with open(JOURNAL_WRITE_TMPL_FILE, 'r') as f:
        journal_tmpl = f.read()
    section = config['WriteTemplate']
    taskline_tmpl = section['TASKLINE']
    date_tmpl = section['DATE']
    date_reg = Journal.date_reg(date_tmpl)
    time_tmpl = section['TIME']
    time_reg = Journal.time_reg(time_tmpl)
    times_delim = section['TIMES_DELIM']

    # ツリーからジャーナルテキストを作成する
    journal = Journal.journal(date, new_tree, memo, journal_tmpl, taskline_tmpl,
            time_tmpl, times_delim, infinite)

    # ジャーナルテキストをファイルに書き出す
    with open(journal_file, 'w') as f:
        f.write(journal)

    # ジャーナル書き出しに使用した設定を次回以降の読み出し設定にセットする
    with open(JOURNAL_READ_TMPL_FILE, 'w') as f:
        f.write(journal_tmpl)
    section = config['ReadTemplate']
    section['TASKLINE'] = taskline_tmpl
    section['DATE'] = date_tmpl
    section['TIME'] = time_tmpl
    section['TIMES_DELIM'] = times_delim
    with open(JOURNAL_CONF_FILE, 'w') as f:
        config.write(f)

    return new_tree

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
