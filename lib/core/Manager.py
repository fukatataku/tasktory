# -*- encoding:utf-8 -*-

import os, pickle

class Manager:

    PROFILE_NAME = '.tasktory'

    @staticmethod
    def get(task_name, parent_dir):
        """ファイルシステムから単一のタスクトリを取り出す
        親子の解決はしない
        """
        profile = os.path.join(parent_dir, task_name, PROFILE_NAME)

        # プロファイルが無ければNoneを返す
        if not os.path.isfile(profile):
            return None

        # プロファイルからタスクトリのデータを復元する
        with open(profile, 'r') as f:
            task = pickle.load(f)

        # タスクトリ名を復元する
        task.name = task_name

        return task

    @staticmethod
    def put(task, parent_dir):
        """単一のタスクトリをファイルシステムに変換して保存する
        """
        # タスクトリのコピーを作成する
        tmp_task = task.copy()

        # タスクトリ名を基にディレクトリを作る
        task_dir = os.path.join(parent_dir, tmp_task.name)
        tmp_task.name = None
        ps.makedirs(path)

        # 親タスクトリと子タスクトリのデータを削除する
        tmp_task.parent = None
        tmp_task.children = None

        # タスクトリのデータをプロファイルに保存する
        profile = os.path.join(task_dir, PROFILE_NAME)
        with open(profile, "w") as f:
            pickle.dump(tmp_task, f)

        del tmp_task
        return task_dir

    @staticmethod
    def get_tree(task_name, parent_dir):
        """タスクトリの実体であるファイルシステムからタスクトリツリーを取得する
        """
        # タスクトリを復元する
        task = get(task_name, parent_dir)
        if task is None: return None

        # タスクトリに含まれるディレクトリ一覧を取得する
        task_dir = os.path.join(parent_dir, task_name)
        dirs = [p for p in os.listdir(task_dir) if os.path.isdir(p)]

        # 子タスクトリを復元し、子に加える
        for d in dirs:
            child = get_tree(d, task_dir)
            if child is None: continue
            task.append(child)

        return task

    @staticmethod
    def put_tree(node, parent_dir):
        """タスクツリーをファイルシステムに書き込む
        """
        task_dir = put(node, parent_dir)
        for n in node:
            put_tree(n, task_dir)

    @staticmethod
    def commit(node, parent_dir):
        """引数として渡したタスクトリツリーをファイルシステムに反映する
        作業時間の整合性などもチェックし、不正な場合はエラーを出す
        """
        org = get(node.name, parent_dir)
        new = org + node
        task_dir = put(new, parent_dir)
        for n in node:
            commit(n, task_dir)
