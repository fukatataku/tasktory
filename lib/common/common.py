# -*- encoding:utf-8 -*-

import os

THIS_DIR = os.path.dirname(os.path.absname(__file__))
HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))
CONF_DIR = os.path.join(HOME_DIR, 'conf')
TMPL_DIR = os.path.join(HOME_DIR, 'template')

JOURNAL_CONF_FILE = os.path.join(CONF_DIR, 'journal.conf')
JOURNAL_TMPL_FILE = os.path.join(TMPL_DIR, 'journal.tmpl')

def arch(param, par_type):
    """変数の型をまとめて判定する
    arch((1, 'hoge', True, [10, 20], [0, 'fuga']), (int, str, bool, [int, int], list)) -> True
    arch((1, 2, 3), (int, str, int)) -> False
    arch(1, int) -> True
    arch(None, None) -> True
    """
    # par_type に許されるのは type, list, tuple, Noneのみ
    if not isinstance(par_type, (type, list, tuple, type(None))):
        raise TypeError("無効な型が指定されました")

    # List of type OR tuple of type
    elif isinstance(par_type, (list, tuple)):
        if not type(param) == type(par_type):
            return False
        if not len(param) == len(par_type):
            return False

        rets = [check_arch(p, par_type[i]) for i,p in enumerate(param)]
        if [r for r in rets if not r]:
            return False
        else:
            return True

    # NoneTypeはNoneで指定可能
    elif par_type == None:
        return True if param == None else False

    else:
        return isinstance(param, par_type)

def rexec(node, exec_func, iter_func=iter,
        exec_cond_func=lambda n:True, rec_cond_func=lambda n:True):
    """ツリー構造のオブジェクトに対して再起的に処理を行う
    """
    # 実行条件関数の結果が真なら、関数を実行する
    if exec_cond_func(node):
        exec_func(node)

    # 再起条件関数の結果が偽なら、終了する
    if not rec_cond_func(node):
        return

    # 子ノードに再起的に適用する
    for c in iter_func(node):
        rexec(c, exec_func, iter_func, exec_cond_func, rec_cond_func)

    return

class ClassProperty(property):
    """propertyデコレータのクラス変数版
    class Foo(metaclass=PropertyMeta):
        __bar = None

        @ClassProperty
        def bar(self):
            return self.__bar

        @bar.setter
        def bar(self, value)
            self.__bar = value
    """
    pass

class PropertyMeta(type):
    """クラスプロパティデコレータ実装のためのメタクラス
    """
    def __new__(cls, name, bases, namespace):
        props = [(k,v) for k,v in namespace.items() if type(v) == ClassProperty]
        for k, v in props:
            setattr(cls, k, v)
            del namespace[k]
        return type.__new__(cls, name, bases, namespace)
