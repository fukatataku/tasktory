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

# ポップアップメッセージ
ERROR_JNL_READ = 0
ERROR_JNL_DUPL = 1
ERROR_JNL_OVLP = 2
INFO_JNL_START = 3
INFO_JNL_END = 4
INFO_FS_START = 5
INFO_FS_END = 6
POPMSG_MAP = {
        ERROR_JNL_READ : ('ERROR', 'ジャーナルの読み込みに失敗しました'),
        ERROR_JNL_DUPL : ('ERROR', '同名のタスクが記載されています'),
        ERROR_JNL_OVLP : ('ERROR', '作業時間が重複しています'),
        INFO_JNL_START : ('INFO', 'ジャーナルへの書き出しを開始します'),
        INFO_JNL_END : ('INFO', 'ジャーナルへの書き出しが完了しました'),
        INFO_FS_START : ('INFO', 'ファイルシステムへの書き出しを開始します'),
        INFO_FS_END : ('INFO', 'ファイルシステムへの書き出しが完了しました'),
        }
