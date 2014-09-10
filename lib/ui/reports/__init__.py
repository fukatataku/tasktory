# -*- encoding:utf-8 -*-

def __modules__():
    """パッケージ内に含まれるモジュールのリストを返す
    """
    from os.path import dirname, basename, splitext, join
    from glob import glob
    from importlib import import_module

    name_list = [__package__+'.'+splitext(basename(p.replace('\\', '/')))[0]
            for p in glob(join(dirname(__file__), '*.py')) if p != __file__]
    modules = [import_module(n) for n in NAME_LIST]

    return modules
