#!C:/python/python3.4/python
#!python3
# -*- encoding:utf-8 -*-

from lib.common.exceptions import *

if __name__ == '__main__':
    print('=== Warning ===')
    for e in [e for e in ExceptionMeta.classes() if issubclass(e, TasktoryWarning)]:
        print(e)
    print('=== Error ===')
    for e in [e for e in ExceptionMeta.classes() if issubclass(e, TasktoryError)]:
        print(e)
    pass
