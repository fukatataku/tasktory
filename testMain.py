#!python3
#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

from lib.common.RWTemplate import RWTemplate

if __name__ == '__main__':
    tmpl = RWTemplate('%YEAR/%MONTH/%DAY')
    print(tmpl.parse('2014/07'))
    pass
