#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import os, configparser
from string import Template

from lib.core.Manager import Manager
from lib.ui.Report import Report
from lib.common.common import MAIN_CONF_FILE

def main():
    # コンフィグを読み出す
    configparser.ConfigParser()
    config.read(MAIN_CONF_FILE)
    root = config['MAIN']['ROOT']
    profile_name = config['MAIN']['PROFILE_FILE']
    report_dir = config['REPORT']['REPORT_DIR']
    report_name_tmpl = Template(config['REPORT']['REPORT_NAME'])

    # ファイルシステムからタスクトリを読み出す
    tree = Manager.get_tree(root, profile_name)

    # 日付
    today = datetime.date.today()

    # レポートを作成する
    for report_name, report_text in Report.report_all(today, tree):
        # 保存用パスを作成する
        save_file_name = report_name_tmpl.substitute(
                NAME=name, YEAR=today.year, MONTH=today.month, DAY=today.day)
        save_dir = os.path.join(report_dir, report_name)
        save_file = os.path.join(save_dir, save_file_name)

        # ディレクトリを作成する
        os.makedirs(save_dir)

        # レポートをファイルに書き出す
        with open(save_file, 'w') as f:
            f.write(report_text)

    return

if __name__ == '__main__':
    main()
