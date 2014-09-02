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
        return self.name

    def __str__(self):
        return self.name

    #==========================================================================
    # 比較／テスト
    #==========================================================================
    def __lt__(self, other):
        """タイムスタンプの大小に基づいて比較する
        """
        return self.timestamp < other.timestamp

    def __le__(self, other):
        return self.timestamp <= other.timestamp

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
        return self.timestamp > other.timestamp

    def __ge__(self, other):
        return self.timestamp >= other.timestamp

    def __bool__(self):
        return True

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def __len__(self):
        """ツリー内の全ノード数を返す
        """
        return 1 + sum([c.__len__() for c in self.children])

    def __getitem__(self, key):
        """IDまたはタスクトリ名でツリー内検索を行う
        """
        if isinstance(key, int):
            test = self.ID == key
        elif isinstance(key, str):
            test = self.name == key
        elif isinstance(key, Tasktory):
            test = self.ID == key.ID
        else:
            raise TypeError()

        if test: return self
        for c in self.children:
            task = c.__getitem__(key)
            if task: return task
        raise IndexError()

    def __setitem__(self, key, value):
        """IDまたはタスクトリ名でツリー内のノードを指定し、valueに置き換える
        本メソッドは上書きが目的であり、新規に追加する場合はappendを使うこと
        """
        self[key].jack(value)

    def __iter__(self):
        """自身に含まれる全タスクトリを直列に並べリスト化して返す
        """
        ret = [self]
        for s in [c.__iter__() for c in self.children]: ret += s
        return ret

    def __contains__(self, item):
        """タスクツリー内にitemが含まれるか調べる
        """
        if isinstance(item, int):
            test = self.ID == item
        elif isinstance(item, str):
            test = self.name == item
        elif isinstance(item, Tasktory):
            test = self.ID == item.ID
        else:
            raise TypeError()

        if test: return True
        return any([item in c for c in self.children])

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def __add__(self, other):
        """２つのタスクトリをマージする
        """
        # タスクトリIDは同じでなければならない
        if not self.ID == other.ID:
            raise ValueError()

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

        # 作業時間は結合する。
        ret.timetable = [(s,t) for s,t in old.timetable + new.timetable]
        # TODO: 重複の解決をどこでするか決める

        # ステータスはタイムスタンプが新しい方を使用する
        ret.status = new.status

        # 親タスクトリは新しい方を優先する
        ret.parent = new.parent if new.parent else old.parent

        # 子タスクトリリスト
        _ = new.children + old.children
        while _:
            c = _.pop(0)
            ret.append((c + _.pop(_.index(c))) if c in _ else c.copy())

        # コメントはタイムスタンプが新しい方を使用する
        ret.comments = new.comments

        return ret

    #==========================================================================
    # タスクトリデータ参照メソッド
    #==========================================================================
    def get_path(self, root='/', namefunc=lambda t:t.name):
        """タスクトリのフルパスを返す
        """
        return os.path.join(self.parent.get_path(root, namefunc) if self.parent
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

    #==========================================================================
    # タスクトリデータ変更メソッド
    #==========================================================================
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

    #==========================================================================
    # 抽象データ参照メソッド
    #==========================================================================
    def get(self, key, default=None):
        """タスクトリツリーからタスクトリを検索して返す
        """
        if isinstance(key, int):
            test = self.ID == key
        elif isinstance(key, str):
            test = self.name == key
        elif isinstance(key, Tasktory):
            test = self.ID == key.ID
        else:
            raise TypeError()

        if test: return self
        for c in self.children:
            task = c.get(key, default)
            if task: return task

        return default

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

    #==========================================================================
    # 抽象データ変更メソッド
    #==========================================================================
    def commit(self, delta):
        """タスクツリーに差分を含むタスクをコミットする
        selfはタスクツリー、deltaは単一のタスクである事を想定している
        該当するタスクが見つからない場合はFalseを返す
        """
        # taskはTasktoryでなければならない
        if not isinstance(task, Tasktory): raise TypeError()

        # 該当するタスクを探す
        task = self.get(delta.ID)
        if task is None: return False

        # 差分をマージしたタスクを作成する
        new_task = task + delta

        # マージしたタスクで上書きする
        self[new_task.ID] = new_task

        return True

    def jack(self, other):
        """selfのデータをotherのもので上書きする
        """
        # otherはTasktoryでなければならない
        if not isinstance(other, Tasktory): raise TypeError()

        # IDは同一でなければならない
        if self.ID != other.ID: raise ValueError()

        self.name = other.name
        self.timestamp = other.timestamp
        self.deadline = other.deadline
        self.start = other.start
        self.end = other.end
        self.timetable = [(s,t) for s,t in other.timetable]
        self.status = other.status
        self.parent = other.parent
        self.children = [c for c in other.children]
        self.comments = other.comments
        return
