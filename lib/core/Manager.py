# -*- encoding:utf-8 -*-

import os, pickle, configparser

from lib.core.Tasktory import Tasktory
from lib.common.RWTemplate import RWTemplate
from lib.common.common import DATA_DIR
from lib.common.common import REPORT_CONF_FILE

class Manager:

    MAX_ID_FILE = os.path.join(DATA_DIR, 'max_id')

    PROFILE_NAME = '.tasktory'
    LOCK_FILE_NAME = '.lock'

    @staticmethod
    def config(section_name):
        """コンフィグを読み込み、加工して返す
        """
        config = configparser.ConfigParser()
        config.read(REPORT_CONF_FILE)
        section = config['section_name']

        # ディレクトリ名テンプレート
        dir_name_tmpl = RWTemplate(section['DIR_NAME_TMPL'])

        ret = (dir_name_tmpl,)
        return ret

    @staticmethod
    def tasktory(name):
        """Tasktoryの作成を仲介し、ID（通し番号）を管理する
        """
        # 最大ID値を取得する
        if os.path.isfile(MAX_ID_FILE):
            with open(MAX_ID_FILE, 'r') as f:
                max_id = int(f.read())
        else:
            max_id = 0

        # タスクトリを新規作成する
        task = Tasktory(max_id, name)

        # 最大ID値を更新して保存する
        max_id += 1
        with open(MAX_ID_FILE, 'w') as f:
            f.write(str(max_id))

        return task

    @staticmethod
    def dirname(task, dir_name_tmpl):
        """タスクトリのディレクトリ名を取得する
        """
        return dir_name_tmpl.substitute({'ID': task.ID, 'NAME': task.name})

    @staticmethod
    def is_tasktory(path):
        """指定されたパスがタスクトリかどうかを返す
        """
        return os.path.isfile(os.path.join(path, PROFILE_NAME))

    @staticmethod
    def list_tasktory(path):
        """指定されたパスの下にあるサブタスクトリのパスのリストを返す
        """
        dirs = [os.path.join(path, p) for p in os.listdir(path)]
        return [p for p in dirs if is_tasktory(p)]

    @staticmethod
    def get(path):
        """指定されたパスのタスクトリを取得する
        指定されたパスがタスクトリでなければNoneを返す
        """
        # 指定されたパスがタスクトリかどうかチェックする
        if not is_tasktory(path):
            return None

        # タスクトリを復元する
        with open(os.path.join(path, PROFILE_NAME), 'r') as profile:
            task = pickle.load(profile)

        return task

    @staticmethod
    def put(task, root, dir_name_tmpl):
        """タスクトリを保存する
        rootにはタスクトリツリーのルートパスを指定する
        ※タスクトリの親パスではなく、最上位タスクの親ディレクトリ
        """
        # タスクトリのフルパスを取得する
        path = task.get_path(root, lambda t:dirname(t, dir_name_tmpl))

        # ディレクトリを作成する
        os.makedirs(path)

        # 不要なデータを削除する
        tmp_task = task.copy()
        tmp_task.parent = None
        tmp_task.children = None

        # タスクトリを保存する
        with open(os.path.join(path, PROFILE_NAME), 'w') as profile:
            pickle.dump(tmp_task, profile)

    @staticmethod
    def get_tree(path):
        """指定したパス以下のタスクトリツリーを取得する
        """
        # タスクトリを復元する
        task = get(path)
        if task is None: return None

        # サブタスクトリを復元する
        children = [get_tree(p) for p in list_tasktory(path)]
        [task.append(c) for c in children if c is not None]

        return task

    @staticmethod
    def put_tree(tree, root, dir_name_tmpl=None):
        """タスクトリツリーを保存する
        rootにはタスクトリツリーのルートパスを指定する
        ※タスクトリツリーの親パスではなく、最上位タスクの親ディレクトリ
        """
        # ディレクトリ名テンプレートを解決する
        if dir_name_tmpl is None:
            dir_name_tmpl = Manager.config('WriteTemplate')

        # タスクトリを保存する
        put(tree, root, dir_name_tmpl)

        # サブタスクトリを保存する
        [put_tree(c, root, dir_name_tmpl) for c in tree]

    @staticmethod
    def check(tree):
        # treeのタイムテーブルを取得する
        timetable = tree.get_whole_timetable()

        # タイムテーブルを変換する
        timetable = [(s, s+t) for s,t in timetable]

        # タイムテーブルを開始エポック秒でソートする
        timetable = sorted(timetable, key=lambda t:t[0])

        # 作業時間にオーバーラップがないか確認する
        last_time = 0
        for s,e in timetable:
            if s < last_time: return False
            last_time = e

        return True

    @staticmethod
    def lock(root):
        lock_file = os.path.join(root, LOCK_FILE_NAME)

        # 既にロックされているかどうか確認する
        if os.path.exists(lock_file):
            # ロックしているのが自分自身ならロックした事にして終了する
            with open(lock_file, 'r') as f:
                pid = int(f.read())
            return True if pid == os.getpid() else False

        # ロックファイルを作成する
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
            return True

    @staticmethod
    def unlock(root):
        """ロックを解除する
        最終的にロックが解除された状態になればTrueを返す
        """
        lock_file = os.path.join(root, LOCK_FILE_NAME)

        # ロックされていなければ解除されたことにして終了する
        if not os.path.exists(lock_file): return True

        # ロックしているプロセスのIDを取得する
        with open(lock_file, 'r') as f: pid = int(f.read())

        # ロックしているのが自分自身であれば解除する
        if pid == os.getpid():
            os.remove(lock_file)
            return True
        else:
            return False

    @staticmethod
    def is_lock(root):
        """ロックされているかどうか確認する
        """
        lock_file = os.path.join(root, LOCK_FILE_NAME)
        return os.path.exists(lock_file)
