# -*- encoding:utf-8 -*-

import os, pickle
from Tasktory import Tasktory

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class Manager:

    # 各タスクトリのデータを格納するファイル
    PROFILE_NAME = '.tasktory'

    # 最大ID値を保持するファイル $TASKTORY/data/$USERNAME/maxid
    HOME_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
    DATA_DIR_NAME = "data"
    USERNAME = os.environ["USERNAME"]
    MAXID_FILE_NAME = "maxid"
    MAXID_FILE = os.path.join(HOME_DIR, DATA_DIR_NAME,
            USERNAME, MAXID_FILE_NAME)

    @staticmethod
    def tasktory(name, timestamp):
        """Tasktory作成を仲介し、通し番号（ID）を管理する
        """
        # 現在の最大のID値をファイルから取得する
        if os.path.isfile(MAXID_FILE):
            with open(MAXID_FILE, 'r') as f:
                maxid = int(f.read())
        else:
            maxid = 0

        # タスクトリを作成する
        task = Tasktory(maxid, name, timestamp)

        # 最大IDを更新してファイルに保存する
        with open(MAXID_FILE, 'w') as f:
            maxid += 1
            f.write(str(maxid))

        return task

    @staticmethod
    def is_tasktory(path):
        """指定したパスがタスクトリかどうかを判定する
        ".profile"という名前のファイルを含んでいるかどうかで判定する
        """
        profile_path = os.path.join(path, PROFILE_NAME)
        return os.path.isfile(profile_path)

    @staticmethod
    def list_tasktory(path):
        """指定したパスに含まれるタスクトリのパスのリストを取得する
        """
        # パスに含まれるディレクトリパスのリストを取得する
        paths = [os.path.join(path, p) for p in os.listdir(path)]

        # ディレクトリの内、タスクトリのみを取り出す
        paths = [t for t in paths if is_tasktory(t)]

        return paths

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
    def get_v2(path):
        """指定されたパスのタスクトリを取得する。
        タスクトリでなければNoneを返す。親子の解決はしない。
        """
        # プロファイルパスを作成する
        profile_path = os.path.join(path, PROFILE_NAME)

        # プロファイルが無ければNoneを返す
        if not os.path.isfile(profile_path):
            return None

        # プロファイルからタスクトリを復元する
        with open(profile_path, 'r') as profile:
            task = pickle.load(profile)

        # タスクトリ名を復元する
        task.name = os.path.basename(path)

        return task

    @staticmethod
    def get_v3(path, ID=None):
        """
        タスクトリ名変更に対応したgetメソッド
        ・親ディレクトリからIDで検索
        ・pathから親ディレクトリを生成してID>basenameの順で検索
        """
        pass

    @staticmethod
    def put(task, parent_dir):
        """単一のタスクトリを保存する
        """
        # タスクトリのコピーを作成する
        tmp_task = task.copy()

        # タスクトリ名を基にディレクトリを作る
        task_dir = os.path.join(parent_dir, tmp_task.name)
        tmp_task.name = None
        os.makedirs(path)

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
    def put_v2(task, path):
        """単一のタスクトリを保存する
        """
        # タスクトリのコピーを作成する
        tmp_task = task.copy()

        # ディレクトリを作成する
        os.makedirs(path)

        # タスクトリから不要なデータを削除する
        tmp_task.parent = None
        tmp_task.children = None

        # プロファイルのパスを作成する
        profile_path = os.path.join(path, PROFILE_NAME)

        # タスクトリのデータをプロファイルに保存する
        with open(profile_path, 'w') as profile:
            pickle.dump(tmp_task, profile)

        del tmp_task

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
        children = [get_tree(d, task_dir) for d in dirs]
        [task.append(c) for c in children if not c is None]

        return task

    @staticmethod
    def get_tree_v2(path):
        """指定したパスのタスクトリツリーを取得する
        """
        # タスクトリを復元する
        task = get_v2(path)
        if task is None: return None

        # タスクトリに含まれるタスクトリパス一覧を取得する
        subpaths = list_tasktory(os.path.join(path, task.name))

        # サブタスクトリを復元する
        children = [get_tree_v2(p) for p in subpaths]
        [task.append(c) for c in children if c is not None]

        return task

    @staticmethod
    def get_subtree(path, tree):
        """指定したパスのタスクトリツリーを取得する
        ただし、引数treeに含まれないタスクは取得しない
        """
        # タスクトリを復元する
        if tree.name != os.path.basename(path): return None
        task = get_v2(path)
        if task is None: return None

        # タスクトリに含まれるタスクトリパス一覧を取得する
        subpaths = list_tasktory(os.path.join(path, task.name))
        subpaths = [p for p in subpaths if os.path.basename(p) in tree]

        # サブタスクトリを復元する
        children = [get_tree_v2(p) for p in subpaths]
        [task.append(c) for c in children if c is not None]

        return task

    @staticmethod
    def get_subtree_v2(path, tree):
        """指定したパスのタスクトリツリーを取得する
        ただし、引数Treeに含まれないタスクトリは取得しない
        タスクトリの同定にはIDを使用する
        """
        # タスクトリを復元する
        task = get_v2(path)

        # タスクトリが取得できないか、できてもIDが違う場合

    @staticmethod
    def put_tree(node, parent_dir):
        """タスクツリーをファイルシステムに書き込む
        """
        task_dir = put(node, parent_dir)
        for n in node: put_tree(n, task_dir)

    @staticmethod
    def commit(node, parent_dir):
        """引数として渡したタスクトリツリーをファイルシステムに反映する
        作業時間の整合性などもチェックし、不正な場合はエラーを出す
        """
        pass

    @staticmethod
    def check(tree):
        """ツリー全体で作業記録に矛盾等がないかチェックする
        ・同じ時間の作業が複数ないか
        ・作業時間に空きが無いか（コアタイムを知っている必要がある）
        """
        # 全タスクトリからタイムテーブルを取得する
        timetable = tree.get_whole_timetable()

        # タイムテーブルを変換する
        # (開始エポック秒, 作業時間) -> (開始エポック秒, 終了エポック秒)
        timetable = [(s, s+t) for s,t in timetable]

        # タイムテーブルを開始エポック秒でソートする
        timetable = sorted(timetable, key=lambda t:t[0])

        # タイムテーブルにオーバーラップがないか確認する
        last_time = 0
        for t in timetable:
            if t[0] < last_time: return False
            last_time = t[1]

        return True
