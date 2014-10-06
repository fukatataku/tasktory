#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import itertools

if __name__ == '__main__':
    print('OK')
    t = [
            ('NAME_1', 'VALUE_2'),
            ('NAME_2', 'VALUE_2'),
            ('NAME_3', 'VALUE_3'),
            ('NAME_4', 'VALUE_4'),
            ]

    d = dict((i,n) for i,(n,v) in enumerate(t))
    print(d)
