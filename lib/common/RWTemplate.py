# -*- encoding:utf-8 -*-

import re
from string import Template

class RWTemplate(Template):
    """読み書きテンプレート
    string.Templateに、テンプレートによる読み込み機能を追加したもの
    tmpl = RWTemplate('%YEAR年%{MONTH}月%DAY日')
    tmpl.parse('2014年4月1日') -> {'YEAR':'2014', 'MONTH':'4', 'DAY':'1'}
    tmpl.parse('年4月1日') -> {'YEAR':'', 'MONTH':'4', 'DAY':'1'}
    tmpl.substitute({'YEAR':'2014', 'MONTH':'4', 'DAY':'1'}) -> '2014年4月1日'
    ※ デリミタの変更は禁止
    """

    delimiter = '%'

    __esc_reg = re.compile('([.^$*+?{}\\\[\]|()])')
    __hold_reg = re.compile(r'%(\\\{)?([A-Za-z_][A-Za-z0-9_]*)(?(1)\\\})')

    def __init__(self, template):
        super().__init__(template)

        pattern = template

        # 特殊な文字をエスケープする
        pattern = self.__esc_reg.sub(r'\\\1', template)

        # %% をを退避する
        pattern_list = pattern.split('%%')

        # プレースホルダーを正規表現に変換する
        pattern_list = [self.__hold_reg.sub(r'(?P<\2>.*?)', s)
                for s in pattern_list]

        # % を復帰させる
        pattern = '%'.join(pattern_list)

        # 行頭に \A, 行末に \Z を追加する
        self.pattern = r'\A' + pattern + r'\Z'

        # コンパイルする
        self.tmpl_reg = re.compile(self.pattern, re.DOTALL)

    def parse(self, string):
        m = self.tmpl_reg.match(string)
        if not m: raise ValueError()
        return m.groupdict()
