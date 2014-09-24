# -*- encoding:utf-8 -*-

import os, pickle

class Manager:

    #==========================================================================
    # ディレクトリ → タスクトリ変換メソッド
    #==========================================================================
    @staticmethod
    def get_tree(root, profile_name):
        """指定したパス以下のタスクトリツリーを取得する
        """
        # タスクトリを復元する
        task = Manager.get(root, profile_name)
        if task is None: return None

        # サブタスクトリを復元する
        children = [Manager.get_tree(os.path.join(root, p), profile_name)
                for p in os.listdir(root)]
        [task.append(c) for c in children if c is not None]

        return task

    @staticmethod
    def get(path, profile_name):
        """指定されたパスからタスクトリを作成して返す
        指定されたパスがタスクトリでなければNoneを返す
        """
        # プロファイルのパスを作成する
        profile = os.path.join(path, profile_name)

        # タスクトリプロファイルが存在するか確認する
        if not os.path.isfile(profile): return None

        # タスクトリを復元する
        with open(profile, 'r') as f:
            try:
                task = pickle.load(f)
            except pickle.UnpicklingError:
                return None

        return task

    #==========================================================================
    # タスクトリ → ディレクトリ変換メソッド
    #==========================================================================
    @staticmethod
    def put(root, task, profile_name):
        """タスクトリをファイルシステムに保存する
        """
        # タスクトリのフルパスを取得する
        path = task.path(root)

        # ディレクトリを作成する
        os.makedirs(path)

        # 保存用のオブジェクトを作成する
        tmp = task.copy()

        # タスクトリを保存する
        with open(os.path.join(path, PROFILE_NAME), 'w') as f:
            pickle.dump(tmp, f)

        return

    #==========================================================================
    # タスクトリツリー診断メソッド
    #==========================================================================
    @staticmethod
    def overlap(tree):
        """ツリー全体のタイムテーブルに重複する箇所が無いか確認する
        重複がある場合はTrue、無い場合はFalseを返す
        """
        # タイムテーブルを取得し、開始エポック秒でソートする
        table = sorted(sum([n.timetable for n in tree], []), key=lambda t:t[0])

        # 作業時間に重複がないか確認する
        last = 0
        for s,t in table:
            if s < last: return True
            last = s + t
        return False