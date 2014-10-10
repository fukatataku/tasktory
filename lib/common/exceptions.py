#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

#==============================================================================
# メタクラスと基底クラス
#==============================================================================
class ExceptionMeta(type):
    """クラスに自動でIDを振り、作成したクラスへの参照を保持するメタクラス"""
    __num = 0
    __classes = []
    def __new__(cls, name, bases, namespace):
        namespace['ID'] = cls.__num
        cls.__num += 1
        created_class =  type.__new__(cls, name, bases, namespace)
        cls.__classes.append(created_class)
        return created_class

    @classmethod
    def classes(cls):
        return cls.__classes

class TasktoryException(Exception, metaclass=ExceptionMeta):
    """タスクトリシステムで使用される例外の基底クラス"""
    MSG = ''

#==============================================================================
# ジャーナル関連の例外
#==============================================================================
class JournalReadTemplateReadFailedException(TasktoryException):
    MSG = 'ジャーナル読み込みテンプレートの読み込みに失敗しました'

class JournalWriteTemplateReadFailedException(TasktoryException):
    MSG = 'ジャーナル書き込みテンプレートの読み込みに失敗しました'

class JournalReadTemplateUpdateFailedException(TasktoryException):
    MSG = 'ジャーナル書き込みテンプレートの更新に失敗しました'

class JournalReadConfigReadFailedException(TasktoryException):
    MSG = 'ジャーナル読み込みコンフィグの読み込みに失敗しました'

class JournalWriteConfigReadFailedException(TasktoryException):
    MSG = 'ジャーナル書き込みコンフィグの読み込みに失敗しました'

class JournalReadConfigUpdateFailedException(TasktoryException):
    MSG = 'ジャーナル読み込みコンフィグの更新に失敗しました'

class JournalFileNotFoundException(TasktoryException):
    MSG = 'ジャーナルファイルが見つかりません'

class JournalCreateTextFailedException(TasktoryException):
    MSG = 'ジャーナルテキストの作成に失敗しました'

class JournalReadFailedException(TasktoryException):
    MSG = 'ジャーナルの読み込みに失敗しました'

class JournalWriteFailedException(TasktoryException):
    MSG = 'ジャーナルの書き込みに失敗しました'

class JournalDuplicateTasktoryException(TasktoryException):
    MSG = 'ジャーナル中のタスクトリに重複があります'

class JournalOverlapTimetableException(TasktoryException):
    MSG = 'ジャーナル中の作業時間に重複があります'

#==============================================================================
# レポート関連の例外
#==============================================================================
class ReportCreateTextFailedException(TasktoryException):
    MSG = 'レポートテキストの作成に失敗しました'

class ReportWriteFailedException(TasktoryException):
    MSG = 'レポートの作成に失敗しました'

#==============================================================================
# ファイルシステム関連の例外
#==============================================================================
class FSReadTreeFailedException(TasktoryException):
    MSG = 'タスクトリツリーの読み込みに失敗しました'

class FSWriteTreeFailedException(TasktoryException):
    MSG = 'タスクトリツリーの書き込みに失敗しました'

#==============================================================================
# タスクトリ関連の例外
#==============================================================================
class TasktoryMargeFailedException(TasktoryException):
    MSG = 'タスクトリのマージに失敗しました'

class TasktoryOverlapTimetableException(TasktoryException):
    MSG = 'タスクトリツリー中の作業時間に重複があります'

#==============================================================================
# その他の関連の例外
#==============================================================================
class UnknownException(TasktoryException):
    MSG = '失敗しました'
