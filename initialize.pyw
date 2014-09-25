#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import configparser

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager
from lib.common.common import MAIN_CONF_FILE

def main():
    # コンフィグを読み出す
    configparser.ConfigParser()
    config.read(MAIN_CONF_FILE)
    section = config['MAIN']
    root = section['ROOT']
    profile_name = section['PROFILE']

    # ルートタスクトリを作成する
    task = Tasktory('', 3650)

    # ファイルシステムに書き込む
    Manager.put(root, task)

    return

if __name__ == '__main__':
    main()
