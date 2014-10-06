# -*- encoding:utf-8 -*-

class OverlapTimetableException(RuntimeError):
    """ツリー中のタイムテーブルに重複がある場合の例外
    """
    pass

class JournalOverlapTimetableException(RuntimeError):
    """ジャーナル中のタイムテーブルに重複がある場合の例外
    """
    pass

class JournalDuplicateTasktoryException(RuntimeError):
    """ジャーナル中のタスクトリに重複がある場合の例外
    """
    pass
