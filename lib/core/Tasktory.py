# -*- encoding:utf-8 -*-

import os

class Tasktory(object):

    OPEN = 'open'
    WAIT = 'wait'
    CLOSE = 'close'

    def __init__(self, ID, name, timestamp):

        # タスクトリID
        self.ID = ID

        # タスクトリ名（ディレクトリ／フォルダ名に使用できる文字列）
        self.name = name

        # タイムスタンプ（グレゴリオ序数）
        self.timestamp = timestamp

        # 期日（グレゴリオ序数）
        self.deadline = None

        # 開始日（グレゴリオ序数）
        self.start = None

        # 終了日（グレゴリオ序数）
        self.end = None

        # タイムテーブル（開始エポック秒と作業時間（秒）のタプルのリスト）
        self.timetable = []

        # ステータス（OPEN or WAIT or CLOSE）
        self.status = Tasktory.OPEN

        # 親タスクトリ
        self.parent = None

        # 子タスクトリ（リスト）
        self.children = []

        # コメント
        self.comments = ''

        return

    #==========================================================================
    # 文字列表現
    #==========================================================================
    def __repr__(self):
        return

    def __str__(self):
        return

    #==========================================================================
    # 比較／テスト
    #==========================================================================
    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __eq__(self, other):
        if isinstance(other, int):
            return self.ID == other
        elif isinstance(other, str):
            return self.name == other
        elif isinstance(other, Tasktory):
            return self.ID == other.ID
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __bool__(self):
        return True

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def __len__(self):
        return len(self.children)

    def __getitem__(self, key):
        # TODO: int -> index or ID?
        if isinstance(key, (int, slice)):
            return self.children[key]
        elif isinstance(key, str):
            return [c for c in self.children if c.name == key][0]
        else:
            raise TypeError()

    def __iter__(self):
        for child in self.children:
            yield child

    def __contains__(self, item):
        return item in self.children

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def __add__(self, other):
        """２つのタスクトリをマージする
        """
        # タスクトリIDは同じでなければならない
        if not self.ID == other.ID:
            raise ValueError()

        # タスクトリ名は同じでなければならない
        #if not self.name == other.name:
        #    raise ValueError()

        # self, otherをタイムスタンプの大小関係により再アサインする
        old, new = sorted((self, other), key=lambda c:c.timestamp)

        # 新しいタスクトリを作成する
        ret = Tasktory(self.ID, new.name, new.timestamp)

        # 期日はタイムスタンプが新しい方を優先する
        ret.deadline = new.deadline if new.deadline else old.deadline

        # 開始日はタイムスタンプが古い方を優先する
        ret.start = old.start if old.start else new.start

        # 終了日はタイムスタンプが新しい方を使用する
        ret.end = new.end

        # 作業時間は結合する。重複の解決はここではしない
        ret.timetable = [(s,t) for s,t in old.timetable + new.timetable]

        # ステータスはタイムスタンプが新しい方を使用する
        ret.status = new.status

        # 親タスクトリは同じはずなので、どっちでも良い
        ret.parent = self.parent if self.parent else other.parent

        # 子タスクトリリスト
        _ = new.children + old.children
        while _:
            c = _.pop(0)
            ret.append((c + _.pop(_.index(c))) if c in _ else c.copy())

        # コメントはタイムスタンプが新しい方を使用する
        ret.comments = new.comments

        return ret

    #==========================================================================
    # タスクトリメソッド
    #==========================================================================
    #def get_path(self, root='/'):
        #"""タスクトリのフルパスを返す
        #"""
        #return os.path.join(self.parent.get_path(root) if self.parent
                #else root, self.name)

    def get_path(self, root='/', namefunc=lambda t:t.name):
        """タスクトリのフルパスを返す
        """
        return os.path.join(self.parent.get_path(root) if self.parent
                else root, namefunc(self))

    def get_last_timestamp(self):
        """子タスクを含めた、最新のタイムスタンプを取得する
        """
        return max([self.timestamp] +
                [c.get_last_timestamp() for c in self.children])

    def get_time(self):
        """合計作業時間（秒）を返す
        """
        return sum(t for _,t in self.timetable)

    def get_total_time(self):
        """子タスクトリも含めた作業時間の合計を取得する
        """
        return self.get_time() +\
                sum([c.get_total_time() for c in self.children])

    def get_whole_timetable(self):
        """自身と子孫の全タイムテーブルを連結して返す
        """
        return self.timetable +\
                sum([c.get_whole_timetable() for c in self.children], [])

    def add_time(self, start, sec):
        """作業時間を追加する
        初めて作業時間が追加された場合は開始日が記録される
        start - 作業開始時刻をエポック秒で指定する
        time  - 作業時間を秒で指定する
        """
        if not self.timetable and sec > 0:
            self.start = self.timestamp
        self.timetable.append((start, sec))
        return self

    def append(self, child):
        """子タスクトリリストにタスクトリを加える
        子タスクトリの親タスクトリに自身をセットする
        """
        self.children.append(child)
        child.parent = self
        return self

    def is_open(self):
        """ステータスがOPENならTrueを返す
        """
        return self.status == Tasktory.OPEN

    def is_wait(self):
        """ステータスがWAITならTrueを返す
        """
        return self.status == Tasktory.WAIT

    def is_close(self):
        """ステータスがCLOSEならTrueを返す
        """
        return self.status == Tasktory.CLOSE

    def open(self):
        """タスクトリを作業中にする
        ステータスがOPENになり、終了日が消去される
        """
        self.status = Tasktory.OPEN
        self.end = None
        return self

    def wait(self):
        """タスクトリを待機状態にする
        ステータスがWAITになり、終了日が消去される
        """
        self.status = Tasktory.WAIT
        self.end = None
        return self

    def close(self):
        """タスクトリを完了する
        ステータスがCLOSEになり、終了日が記録される
        開始日が記録されていない場合は記録する
        """
        self.status = Tasktory.CLOSE
        if self.start is None:
            self.start = self.timestamp
        self.end = self.timestamp
        return self

    def get_level(self):
        """タスクトリの階層を返す
        """
        return self.parent.get_level() + 1 if self.parent else 0

    def copy(self):
        """タスクトリのディープコピーを返す
        """
        task = Tasktory(self.ID, self.name, self.timestamp)
        task.deadline = self.deadline
        task.start = self.start
        task.end = self.end
        task.timetable = [(s,t) for s,t in self.timetable]
        task.status = self.status
        task.parent = self.parent
        task.children = [c.copy() for c in self.children]
        task.comments = self.comments
        return task

    def search(self, ID):
        """指定したIDを子タスクトリから再帰的に探して返す
        存在しなければNoneを返す
        """
        if self.ID == ID: return self
        for c in self.children:
            task = c.search(ID)
            if task is not None:
                return task
        return None
