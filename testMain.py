#!python3
#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import datetime

from lib.core.Manager import Manager
from lib.ui.Journal import Journal

# ファイルパス
# 入出力は全てmainで実施する
from lib.common.common import MAIN_CONF_FILE
from lib.common.common import MANAGER_CONF_FILE
from lib.common.common import MANAGER_DATA_FILE
from lib.common.common import JOURNAL_CONF_FILE
from lib.common.common import JOURNAL_WRITE_TMPL_FILE
from lib.common.common import JOURNAL_READ_TMPL_FILE

def monitor():
    # 今日の日付
    date = datetime.date.today()

    # タスクトリのルートパスを取得する
    main_config = configparser.ConfigParser()
    main_config.read(MAIN_CONF_FILE)
    root = main_config['MAIN']['ROOT']
    del main_config

    # タスクツリーを読み込む
    tree = Manager.get_tree(root)

    # ジャーナルを生成する
    journal = Journal.journal(tree)
    return

if __name__ == '__main__':
    pass
