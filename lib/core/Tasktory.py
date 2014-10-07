# -*- encoding:utf-8 -*-

import os, uuid

class Tasktory(object):

    # ステータス用定数
    OPEN = 'open'
    WAIT = 'wait'
    CLOSE = 'close'
    CONST = 'const'

    def __init__(self, name, deadline, status=OPEN):

        # タスクトリID
        self.ID = str(uuid.uuid4())

        # タスクトリ名（ディレクトリ／フォルダ名に使用できる文字列）
        self.name = name

        # 期日（グレゴリオ序数）
        self.deadline = deadline

        # ステータス（ステータス用定数）
        self.status = status

        # タイムテーブル（開始エポック秒と作業時間（秒）のタプルのリスト）
        self.timetable = []

        # 親タスクトリ
        self.parent = None

        # 子タスクトリ（リスト）
        self.children = []

        # 種別（任意）
        self.category = None

        # コメント
        self.comments = ''

        return

    #==========================================================================
    # 比較／テスト
    #==========================================================================
    def __lt__(self, other):
        """最新のタイムテーブルの大小に基づいて比較する
        """
        return self.timestamp() < other.timestamp()

    def __le__(self, other):
        return self.timestamp() <= other.timestamp()

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __gt__(self, other):
        return self.timestamp() > other.timestamp()

    def __ge__(self, other):
        return self.timestamp() >= other.timestamp()

    def __bool__(self):
        return True

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def __len__(self):
        """ツリー内の全ノード数を返す
        """
        return 1 + sum([c.__len__() for c in self.children])

    def __iter__(self):
        """ツリー内の全タスクトリを走査する
        """
        yield self
        for child in self.children:
            for c in child: yield c

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def __add__(self, other):
        """２つのタスクトリをマージする
        """
        if self != other:
            raise ValueError()

        # self, otherをタイムスタンプの大小関係により再アサインする
        old, new = sorted((self, other))

        # 期日は新しい方を優先する
        deadline = old.deadline if new.deadline is None else new.deadline

        # 新しいタスクトリを作成する
        # 名前、期日、ステータスは新しい方を使用する
        ret = Tasktory(new.name, deadline, new.status)

        # IDはselfを使用する
        ret.ID = self.ID

        # 作業時間は結合する。
        for s,t in old.timetable + new.timetable: ret.add_time(s,t)

        # 親タスクトリは新しい方を優先する
        ret.parent = new.parent if new.parent else old.parent

        # 子タスクトリリスト
        _ = other.children + self.children
        while _:
            c = _.pop(0)
            ret.append((_.pop(_.index(c)) + c) if c in _ else c.deepcopy())

        # 種別は新しい方を優先する
        ret.category = old.category if new.category is None else new.category

        # コメントは新しい方を使用する
        ret.comments = new.comments

        return ret

    #==========================================================================
    # タスクトリ参照メソッド
    #==========================================================================
    def get(self, name, default=None):
        """子タスクトリから名前で検索する
        """
        children = [c for c in self.children if c.name == name]
        return children[0] if children else default

    def total_time(self):
        """合計作業時間（秒）を返す
        """
        return sum(t for _,t in self.timetable)

    def timestamp(self):
        """タイムテーブルの中から最も大きい終了エポック秒を返す
        作業時間が無い場合は0を返す
        """
        return sum(sorted(self.timetable, key=lambda t:t[0])[-1])\
                if self.timetable else 0

    def copy(self):
        """単一タスクトリのディープコピーを返す（親と子を含まない）
        """
        task = Tasktory(self.name, self.deadline, self.status)
        task.ID = self.ID
        task.timetable = [(s,t) for s,t in self.timetable]
        task.category = self.category
        task.comments = self.comments
        return task

    #==========================================================================
    # タスクトリ変更メソッド
    #==========================================================================
    def add_time(self, start, sec):
        """作業時間を追加する
        start - 作業開始時刻をエポック秒で指定する
        sec  - 作業時間を秒で指定する
        """
        if (start, sec) not in self.timetable:
            self.timetable.append((start, sec))
        return self

    def append(self, child):
        """子タスクトリリストにタスクトリを加える
        子タスクトリの親タスクトリに自身をセットする
        """
        self.children.append(child)
        child.parent = self
        return self

    def wash(self, other):
        """selfのデータをotherのもので上書きする
        """
        # otherはTasktoryでなければならない
        if not isinstance(other, Tasktory): raise TypeError()

        self.ID = other.ID
        self.name = other.name
        self.deadline = other.deadline
        self.timetable = [(s,t) for s,t in other.timetable]
        self.parent = other.parent
        self.children = [c for c in other.children]
        self.status = other.status
        self.category = other.category
        self.comments = other.comments
        return self
    #==========================================================================
    # ツリー参照メソッド
    #==========================================================================
    def find(self, path):
        """ツリー全体からパスで検索する
        例）tree.find('/Project/LargeTask/SmallTask/step1')
        """
        if isinstance(path, str): path = path.rstrip('/').split('/')
        if self.name != path[0]: return None
        if len(path) == 1: return self
        for child in self.children:
            ret = child.find(path[1:])
            if ret is not None: return ret
        return None

    def search(self, test):
        """ツリー全体から条件に一致するタスクトリ全てを返す
        例）期日が一定未満かつCLOSEでないもの
        tree.search(lambda t:t.deadline < DEADLINE and t.status != CLOSE)
        例）特定のIDのタスクトリ
        tree.search(lambda t:t.ID == SPECIFIC_ID)[0]
        """
        ret = [self] if test(self) else []
        for child in self.children: ret += child.search(test)
        return ret

    def path(self, root='/'):
        """タスクトリのフルパスを返す
        """
        return os.path.join(self.parent.path(root) if self.parent
                else root, self.name).replace('\\', '/')

    def level(self):
        """タスクトリの階層を返す
        """
        return self.parent.level() + 1 if self.parent else 0

    def deepcopy(self):
        """タスクトリのディープコピーを返す
        """
        task = Tasktory(self.name, self.deadline, self.status)
        task.ID = self.ID
        task.timetable = [(s,t) for s,t in self.timetable]
        task.parent = self.parent
        task.children = [c.deepcopy() for c in self.children]
        task.category = self.category
        task.comments = self.comments
        return task

    def clip(self, test=lambda t:t.status!=Tasktory.CLOSE):
        """条件に一致するノードと、そのノードへの経路となるノードのみをコピーし
        て返す。
        test : 条件関数。引数としてタスクトリを受け取ってbool値を返す
        """
        children = [c.clip(test) for c in self.children]
        if test(self) or any(children):
            task = self.copy()
            [task.append(c) for c in children if c is not None]
            return task
        return None
