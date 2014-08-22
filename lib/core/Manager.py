# -*- encoding:utf-8 -*-

import os

class Manager:

    @staticmethod
    def get_tree(system_root):
        """タスクトリの実体であるファイルシステムからタスクトリツリーを取得する
        """
        pass

    @staticmethod
    def get_active_tree(system_root):
        """タスクトリの実体であるファイルシステムから未完了のタスクトリツリーを
        取得する
        """
        pass

    @staticmethod
    def commit(tree, system_root):
        """引数として渡したタスクトリツリーをファイルシステムに反映する
        作業時間の整合性などもチェックし、不正な場合はエラーを出す
        """
        pass

