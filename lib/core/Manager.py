# -*- encoding:utf-8 -*-

import os, pickle

class Manager:

    #==========================================================================
    # ディレクトリ → タスクトリ変換メソッド
    #==========================================================================
    @staticmethod
    def get_tree(root, profile_name, rename=False):
        """指定したパス以下のタスクトリツリーを取得する
        """
        # タスクトリを復元する
        task = Manager.get(root, profile_name, rename)
        if task is None: return None

        # サブタスクトリを復元する
        children = [Manager.get_tree(os.path.join(root, p), profile_name, True)
                for p in os.listdir(root)]
        [task.append(c) for c in children if c is not None]

        return task

    @staticmethod
    def get(path, profile_name, rename=True):
        """指定されたパスからタスクトリを作成して返す
        指定されたパスがタスクトリでなければNoneを返す
        """
        # プロファイルのパスを作成する
        profile = os.path.join(path, profile_name)

        # タスクトリプロファイルが存在するか確認する
        if not os.path.isfile(profile): return None

        # タスクトリを復元する
        with open(profile, 'rb') as f:
            try:
                task = pickle.load(f)
                if rename: task.name = os.path.basename(path)
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

        # ディレクトリを無ければ作成する
        if not os.path.isdir(path):
            os.makedirs(path)

        # 保存用のオブジェクトを作成する
        tmp = task.copy()

        # タスクトリを保存する
        with open(os.path.join(path, profile_name), 'wb') as f:
            pickle.dump(tmp, f)

        return

    #==========================================================================
    # ディレクトリ参照メソッド
    #==========================================================================
    @staticmethod
    def listtask(dirpath, profile_name):
        """指定したディレクトリ以下に含まれるタスクトリのパスのリストを取得する
        """
        paths = [os.path.join(dirpath, p).replace('\\', '/')
                for p in os.listdir(dirpath)]
        dirs = [p for p in paths if os.path.isdir(p)]
        tasks = set([p for p in dirs
            if os.path.exists(os.path.join(p, profile_name))])
        return set.union(tasks, *[Manager.listtask(p, profile_name)
            for p in tasks])

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

    @staticmethod
    def same_tree(tree1, tree2):
        """２つのタスクツリーの間に差分があるかどうかを調べる
        差分が無ければTrue、有ればFalseを返す
        """
        if tree1 is tree2: return True
        if tree1 is None or tree2 is None: return False
        for node1, node2 in zip(tree1, tree2):
            if not Manager.same(node1, node2): return False
        return True

    @staticmethod
    def same(task1, task2):
        """２つのタスクトリの間に差分があるかどうかを調べる
        差分が無ければTrue、有ればFalseを返す
        """
        if task1.name != task2.name: return False
        if set(task1.timetable) != set(task2.timetable): return False
        if task1.status != task2.status: return False
        if task1.deadline != task2.deadline: return False
        if task1.category != task2.category: return False
        if task1.comments != task2.comments: return False
        return True
