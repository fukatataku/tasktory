# -*- encoding:utf-8 -*-

class Tasktory(object):

    OPEN = 'open'
    WAIT = 'wait'
    CLOSE = 'close'

    def __init__(self, name, timestamp):

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

        # 作業時間（分）
        self.time = 0

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
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Tasktory):
            return self.name == other.name
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
        # タスクトリ名は同じでなければならない
        if not self.name == other.name:
            raise ValueError()

        # self, otherをタイムスタンプの大小関係により再アサインする
        old, new = sorted((self, other), key=lambda c:c.timestamp)

        # 新しいタスクトリを作成する
        ret = Tasktory(self.name, new.timestamp)

        # 期日はタイムスタンプが新しい方を優先する
        ret.deadline = new.deadline if new.deadline else old.deadline

        # 開始日はタイムスタンプが古い方を優先する
        ret.start = old.start if old.start else new.start

        # 終了日はタイムスタンプが新しい方を使用する
        ret.end = new.end

        # 作業時間は足す
        ret.time = self.time + other.time

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
    def get_last_timestamp(self):
        """小タスクを含めた、最新のタイムスタンプを取得する
        """
        return max([self.timestamp] +
                [c.get_last_timestamp() for c in self.children])

    def add_time(self, time):
        """作業時間を追加する
        初めて作業時間が追加された場合は開始日が記録される
        time - 作業時間を分で指定する
        """
        if self.time == 0 and time > 0:
            self.start = self.timestamp
        self.time += time
        return self

    def get_total_time(self):
        """子タスクトリも含めた作業時間の合計を取得する
        """
        return self.time + sum([c.get_total_time() for c in self.children])

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

    def get_level(self):
        """タスクトリの階層を返す
        """
        return self.parent.get_level() + 1 if self.parent else 0

    def copy(self):
        """タスクトリのディープコピーを返す
        """
        task = Tasktory(self.name, self.timestamp)
        task.deadline = self.deadline
        task.start = self.start
        task.end = self.end
        task.time = self.time
        task.status = self.status
        task.parent = self.parent
        task.children = [c.copy() for c in self.children]
        task.comments = self.comments
        return task
