# -*- encoding:utf-8 -*-

import os

# ユーザー名
user = os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))

# ディレクトリ
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
CONF_DIR = os.path.join(HOME_DIR, 'conf')
DATA_DIR = os.path.join(HOME_DIR, 'data', user)
TMPL_DIR = os.path.join(HOME_DIR, 'template')

# マネージャ関連ファイル
MANAGER_CONF_FILE = os.path.join(CONF_DIR, 'manager.conf')

# ジャーナル関連ファイル
JOURNAL_CONF_FILE = os.path.join(CONF_DIR, 'journal.conf')
JOURNAL_READ_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.read.tmpl')
JOURNAL_WRITE_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.write.tmpl')
