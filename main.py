#!python3
# -*- encoding:utf-8 -*-

from lib.core.Manager import Manager
from lib.ui.Journal import Journal

if __name__ == '__main__':
    # 処理内容
    # ・常駐する
    # ・定期的に以下の処理を行う
    #   ・ファイルシステムからタスクトリツリーを読み込む
    #   ・ジャーナルに更新があれば、コミットする
    #   ・レポートを書き出す
    # ・終了処理は確実にする
    #   どんなタイミングで終了シグナルが送られても適切に終了する
    pass
