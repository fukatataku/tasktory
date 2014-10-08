# -*- encoding:utf-8 -*-

def __reports__():
    """パッケージ内に含まれるレポートの名前とreportメソッドのタプルのリストを
    返す
    """
    from os.path import dirname, basename, splitext, join
    from glob import glob
    from importlib import import_module

    pkg_list = [__package__+'.'+splitext(basename(p.replace('\\', '/')))[0]
            for p in glob(join(dirname(__file__), '*.py')) if p != __file__]
    return [import_module(p) for p in pkg_list]
