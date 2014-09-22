# -*- encoding:utf-8 -*-

import os, pickle

class Manager:

    #==========================================================================
    # タスクトリ作成補助メソッド
    #==========================================================================
    @staticmethod
    def gen_id(filepath):
        """タスクトリのIDを払い出す
        """
        # IDを取得する
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                ID = int(f.read())
        else:
            ID = 0

        # IDを更新する
        with open(filepath, 'w') as f:
            f.write(str(next_id+1))

        return next_id

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
    def put(root, task, profile_name, dir_name_tmpl):
        """タスクトリをファイルシステムに保存する
        """
        # タスクトリのフルパスを取得する
        path = task.path(root, lambda t:Manager.dirname(t, dir_name_tmpl))

        # ディレクトリを作成する
        os.makedirs(path)

        # 不要なデータを削除する
        tmp = task.copy()
        tmp.parent = None
        tmp.children = []

        # タスクトリを保存する
        with open(os.path.join(path, PROFILE_NAME), 'w') as f:
            pickle.dump(tmp, f)

        return

    @staticmethod
    def dirname(task, dir_name_tmpl):
        """タスクトリのディレクトリ名を取得する
        """
        return dir_name_tmpl.substitute({'ID': task.ID, 'NAME': task.name})

    #==========================================================================
    # タスクトリツリー診断メソッド
    #==========================================================================
    @staticmethod
    def overlap(tree):
        """ツリー全体のタイムテーブルに重複する箇所が無いか確認する
        重複がある場合はTrue、無い場合はFalseを返す
        """
        # タイムテーブルを取得し、開始エポック秒でソートする
        timetable = sorted(tree.timetable_of_tree(), key=lambda t:t[0])

        # 作業時間に重複がないか確認する
        last = 0
        for s,t in timetable:
            if s < last: return True
            last = s + t
        return False
