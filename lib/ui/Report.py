# -*- encoding:utf-8 -*-

import lib.ui.reports

class Report:

    @staticmethod
    def reports():
        """レポートの名前とレポートメソッドのタプルのリストを返す
        """
        reports = lib.ui.reports.__reports__()
        return [(m.REPORT_NAME, m.report) for m in reports]
