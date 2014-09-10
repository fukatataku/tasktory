#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import sys, os, time

from lib.core.Manager import Manager
from lib.ui.Journal import Journal

def main():
    # コンフィグ
    # ・タスクトリのルート
    # ・処理のスパン
    # ・ジャーナルのパス

    root = "C:/home/fukata/work"
    span = 10 # １０秒に１回
    journal_path = "C:/home/fukata/journal.txt"

    #======================
    # ループに入る前の準備
    #======================
    # ジャーナルを作成し、ファイルに書き出す
    journal = Journal.journal(Manager.get_tree(root))
    with open(journal_path, 'w') as f:
        f.write(journal)
    del journal

    # ジャーナルのタイムスタンプを取得する
    timestamp = os.stat(journal_path).st_mtime

    while True:
        time.sleep(span)
        # ジャーナルのタイムスタンプを確認する
        if os.stat(journal_path).st_mtime == timestamp: continue
        tasks = Journal.tasktories(journal_path)
        tree = Manager.get_tree(root)

        # コミットする
        for task in tasks:
            target = tree.get(task.ID)
            # TODO targetのタイムテーブルから当日の分を削除する
            new_task = target + task
            target.jack(new_task)

        # 書き出す
        Manager.put_tree(tree)
        # TODO: ジャーナルも書き出す？

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
