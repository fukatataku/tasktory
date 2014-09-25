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
    root = config['MAIN']['ROOT']
    profile_name = config['MAIN']['PROFILE_FILE']
    report_dir = config['REPORT']['REPORT_DIR']

    # ファイルシステムからタスクトリを読み出す
    tree = Manager.get_tree(root, profile_name)

    # レポートを作成する


    return

if __name__ == '__main__':
    main()
