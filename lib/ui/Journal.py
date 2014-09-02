#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import os, sys, configparser

COMMON_DIR = "C:/home/fukata/git/tasktory/lib/common"
sys.path.append(COMMON_DIR)

from RWTemplate import RWTemplate
from common import JOURNAL_CONF_FILE
from common import JOURNAL_TMPL_FILE

class Journal:

    @staticmethod
    def get_journal(filepath):
        return

    @staticmethod
    def put_journal(tasktory, filepath):
        """タスクトリをジャーナルに変換する
        """
        # テンプレートを取得する

        # テンプレートにデータを埋め込む

        # ジャーナルファイルに書き出す
        return

if __name__ == '__main__':
    filepath = "C:/home/fukata/git/tasktory/conf/journal.conf"
    config = configparser.ConfigParser()
    config.read(filepath)
    print(config['Template']['TIME'])
    print(config['Template']['TERM'])
    print(config['Template']['TERM_DELIMITER'])
    print(config['Template']['TASKLINE'])

    print("===================\n")

    filepath = "C:/home/fukata/git/tasktory/template/journal.tmpl"
    with open(filepath, 'r', encoding='utf-8') as f:
        tmpl = f.read()
    print(tmpl)
    print("===================\n")

    template = RWTemplate(tmpl)
    text = template.safe_substitute({'YEAR': '2014', 'MONTH': '9', 'DAY': '2',
        'TODO': 'Todo', 'WAIT': 'Wait', 'DONE': 'Done'})

    print(text)

    filepath = "C:/home/fukata/tmp/journal.txt"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    pass
