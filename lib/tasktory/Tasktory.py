# -*- encoding:utf-8 -*-

class Tasktory(object):

    DO = 'do'
    WAIT = 'wait'
    DONE = 'done'

    def __init__(self, name, deadline=None):

        # タスクトリ名（ディレクトリ／フォルダ名に使用できる文字列）
        self.name = name

        # 期日（グレゴリオ序数）
        self.deadline = deadline

        # 開始日（グレゴリオ序数）
        self.start = None

        # 終了日（グレゴリオ序数）
        self.end = None

        # 作業時間（分）
        self.time = None

        # ステータス（DO, WAIT, DONE）
        self.status = Tasktory.DO

        # 親タスクトリ
        self.parent = None

        # 子タスクトリ（リスト）
        self.children = []

        # コメント
        self.comments = ''

        return
