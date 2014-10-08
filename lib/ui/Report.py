# -*- encoding:utf-8 -*-

import lib.ui.reports

class Report:

    @staticmethod
    def report_map():
        """
        """
        reports = lib.ui.reports.__reports__()
        repo_map = {}
        for i, m in enumerate(reports):
            # key=0は全レポート出力のために使わなずに取っておく
            repo_map[i+1] = (m.REPORT_NAME, m.report)
        return repo_map
