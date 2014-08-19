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

def rexec(obj, exec_func, exec_cond_func=lambda x:True, rec_cond_func=lambda x: True):
    """
    """
    # 実行条件関数が真なら実行する
    if exec_cond_func(obj):
        exec_func(obj)

    # 再帰条件関数が偽なら終了する
    if not rec_cond_func(obj):
        return

    # objが有効なイテレータではないなら終了する
    if not '__iter__' in dir(obj) or isinstance(obj, str):
        return

    # objをイテレータと見なして、再帰する
    for child in obj:
        rexec(child, exec_func, exec_cond_func, rec_cond_func)
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
