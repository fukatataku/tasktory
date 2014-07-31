# -*- encoding:utf-8 -*-

class Tasktory(object):

    DO = 'do'
    WAIT = 'wait'
    DONE = 'done'

    def __init__(self, name, timestamp):

        # タスクトリ名（ディレクトリ／フォルダ名に使用できる文字列）
        self.name = name

        # タイムスタンプ（グレゴリオ序数）
        self.timestamp = timestamp

        # 期日（グレゴリオ序数）
        self.deadline = deadline

        # 開始日（グレゴリオ序数）
        self.start = None

        # 終了日（グレゴリオ序数）
        self.end = None

        # 作業時間（分）
        self.time = 0

        # ステータス（DO, WAIT, DONE）
        self.status = Tasktory.DO

        # 親タスクトリ
        self.parent = None

        # 子タスクトリ（リスト）
        self.children = []

        # コメント
        self.comments = ''

        return

    def __del__(self):
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
        return True

    def __ne__(self, other):
        return True

    def __gt__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __bool__(self):
        return True

    #==========================================================================
    # 属性値アクセス
    #==========================================================================
    def __setattr__(self, name, value):
        return

    #==========================================================================
    # コンテナエミュレート
    #==========================================================================
    def __len__(self):
        return

    def __getitem__(self, key):
        return

    def __setitem__(self, key, value):
        return

    def __delitem__(self, key):
        return

    def __iter__(self):
        return

    def __contains__(self, item):
        return

    #==========================================================================
    # 数値型エミュレート
    #==========================================================================
    def __add__(self, other):
        return

    #==========================================================================
    # メソッド
    #==========================================================================
    def add_time(self, time):
        self.time += time

