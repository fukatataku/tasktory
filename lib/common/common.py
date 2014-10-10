# -*- encoding:utf-8 -*-

import os

# ディレクトリ
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
CONF_DIR = os.path.join(HOME_DIR, 'conf')
TMPL_DIR = os.path.join(HOME_DIR, 'template')
RSRC_DIR = os.path.join(HOME_DIR, 'resource')

# メイン設定ファイル
MAIN_CONF_FILE = os.path.join(CONF_DIR, 'main.conf')

# ジャーナル関連ファイル
JOURNAL_CONF_FILE = os.path.join(CONF_DIR, 'journal.conf')
JOURNAL_READ_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.read.tmpl')
JOURNAL_WRITE_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.write.tmpl')

# トレイアイコン関連ファイル
ICON_PATH = os.path.join(RSRC_DIR, 'tasktory.ico')

# INFOメッセージ
INFO_JNL_START  = 0
INFO_JNL_END    = 1
INFO_FS_START   = 2
INFO_FS_END     = 3
INFO_REPO_START = 4
INFO_REPO_END   = 5
INFO_MAP = {
        INFO_JNL_START  : 'ジャーナルへの書き出しを開始します',
        INFO_JNL_END    : 'ジャーナルへの書き出しが完了しました',
        INFO_FS_START   : 'ファイルシステムへの書き出しを開始します',
        INFO_FS_END     : 'ファイルシステムへの書き出しが完了しました',
        INFO_REPO_START : 'レポートの書き出しを開始します',
        INFO_REPO_END   : 'レポートの書き出しが完了しました',
        }
