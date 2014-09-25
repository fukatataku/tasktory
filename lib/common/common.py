# -*- encoding:utf-8 -*-

import os

# ディレクトリ
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
CONF_DIR = os.path.join(HOME_DIR, 'conf')
TMPL_DIR = os.path.join(HOME_DIR, 'template')

# メイン設定ファイル
MAIN_CONF_FILE = os.path.join(CONF_DIR, 'main.conf')

# ジャーナル関連ファイル
JOURNAL_CONF_FILE = os.path.join(CONF_DIR, 'journal.conf')
JOURNAL_READ_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.read.tmpl')
JOURNAL_WRITE_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.write.tmpl')
