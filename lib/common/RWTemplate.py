#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import re
from string import Template
from functools import reduce

class RWTemplate(Template):
    """読み書きテンプレート
    string.Templateに、テンプレートによる読み込み機能を追加したもの
    tmpl = RWTemplate('%YEAR年%{MONTH}月%DAY日')
    tmpl.parse('2014年4月1日') -> {'YEAR':'2014', 'MONTH':'4', 'DAY':'1'}
    tmpl.parse('年4月1日') -> {'YEAR':'', 'MONTH':'4', 'DAY':'1'}
    tmpl.substitute({'YEAR':'2014', 'MONTH':'4', 'DAY':'1'}) -> '2014年4月1日'
    """

    delimiter = '%'

    __reg_id = re.compile(r'({0}*)({0}{{?([A-Za-z_][A-Za-z0-9_]*)}}?)'\
                          .format(delimiter))

    def __init__(self, template):
        super().__init__(template)
        self.__parse_template(template)

    def __parse_template(self, tmpl):
        tmp = [(p,i) for e,p,i in self.__reg_id.findall(tmpl) if len(e)%2==0]
        holder, self.iD = zip(*tmp) if tmp else ((), ())
        h_indice = RWTemplate.__indice(holder, tmpl)
        c_indice = RWTemplate.__interspace(0, len(tmpl), h_indice)
        self.caret = c_indice[0][1] > 0
        self.dollar = c_indice[-1][0] < len(tmpl)
        self.const = [tmpl[s:e].replace(self.delimiter*2, self.delimiter)
                      for s,e in c_indice if not s==e]

    def parse(self, string):
        c_indice = RWTemplate.__indice(self.const, string)
        v_indice = RWTemplate.__interspace(0, len(string), c_indice)
        values = [string[s:e] for s,e in v_indice]
        if self.caret: values.pop(0)
        if self.dollar: values.pop(-1)
        return dict(zip(self.iD, values))

    @staticmethod
    def __indice(char_list, string):
        ret, last = [], 0
        for c in char_list:
            index = string.index(c, last)
            last = index + len(c)
            ret.append((index, last))
        return ret

    @staticmethod
    def __interspace(start, end, indice):
        return reduce(lambda x,y:x[0:-1] + [(x[-1][0], y[0]),
                      (y[-1], x[-1][-1])], indice, [(start, end)])
