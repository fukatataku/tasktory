# -*- encoding:utf-8 -*-

import os

# ユーザー名
user = os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
CONF_DIR = os.path.join(HOME_DIR, 'conf')
DATA_DIR = os.path.join(HOME_DIR, 'data', user)
TMPL_DIR = os.path.join(HOME_DIR, 'template')

JOURNAL_CONF_FILE = os.path.join(CONF_DIR, 'journal.conf')
JOURNAL_READ_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.read.tmpl')
JOURNAL_WRITE_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.write.tmpl')

MANAGER_CONF_FILE = os.path.join(CONF_DIR, 'manager.conf')

def rexec(node, exec_func, iter_func=iter, iter_sort_func=None,
        exec_cond_func=lambda n:True, rec_cond_func=lambda n:0):
    """ツリー構造のオブジェクトに対して再起的に処理を行う
    node - ツリー構造のオブジェクト
    exec_func - 引数nodeを受け取る任意の処理を行う関数
    iter_func - 引数nodeを受け取って子ノードへのイテレータを返す関数
    iter_sort_func - 子ノードリストをソートする際のsortedのkey
    exec_cond_func - 引数nodeを受け取ってexec_funcを実行するか判定する関数
    rec_cond_func - 引数nodeを受け取って子ノードの再帰実行をするか判定する関数
    """
    # 実行条件関数の結果が真なら、関数を実行する
    if exec_cond_func(node): exec_func(node)

    # 再起条件関数の結果が偽なら、終了する
    if not rec_cond_func(node): return

    # 子ノードに再起的に適用する
    for c in sorted(iter_func(node), key=iter_sort_func):
        rexec(c, exec_func, iter_func, exec_cond_func, rec_cond_func)

    return
