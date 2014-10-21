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
        # 例外IDを付与する
        namespace['ID'] = cls.__num
        cls.__num += 1

        # 例外を作成する
        created_class =  type.__new__(cls, name, bases, namespace)

        # 作成した例外をリストに追加する
        cls.__classes.append(created_class)

        return created_class

    @classmethod
    def classes(cls):
        return cls.__classes

class TasktoryError(Exception, metaclass=ExceptionMeta):
    """タスクトリシステムで使用されるエラーの基底クラス"""
    MSG = ''

class TasktoryWarning(Exception, metaclass=ExceptionMeta):
    """タスクトリシステムで使用される警告の基底クラス"""
    MSG = ''

#==============================================================================
# ジャーナル関連の例外
#==============================================================================
class JournalReadTemplateReadFailedError(TasktoryError):
    MSG = 'ジャーナル読み込みテンプレートの読み込みに失敗しました'

class JournalWriteTemplateReadFailedError(TasktoryError):
    MSG = 'ジャーナル書き込みテンプレートの読み込みに失敗しました'

class JournalReadTemplateUpdateFailedError(TasktoryError):
    MSG = 'ジャーナル書き込みテンプレートの更新に失敗しました'

class JournalReadConfigReadFailedError(TasktoryError):
    MSG = 'ジャーナル読み込みコンフィグの読み込みに失敗しました'

class JournalWriteConfigReadFailedError(TasktoryError):
    MSG = 'ジャーナル書き込みコンフィグの読み込みに失敗しました'

class JournalReadConfigUpdateFailedError(TasktoryError):
    MSG = 'ジャーナル読み込みコンフィグの更新に失敗しました'

class JournalFileNotFoundError(TasktoryError):
    MSG = 'ジャーナルファイルが見つかりません'

class JournalCreateTextFailedError(TasktoryError):
    MSG = 'ジャーナルテキストの作成に失敗しました'

class JournalReadFailedError(TasktoryError):
    MSG = 'ジャーナルの読み込みに失敗しました'

class JournalWriteFailedError(TasktoryError):
    MSG = 'ジャーナルの書き込みに失敗しました'

class JournalDuplicateTasktoryError(TasktoryError):
    MSG = 'ジャーナル中のタスクトリに重複があります'

class JournalOverlapTimetableError(TasktoryError):
    MSG = 'ジャーナル中の作業時間に重複があります'

#==============================================================================
# レポート関連の例外
#==============================================================================
class ReportCreateTextFailedError(TasktoryError):
    MSG = 'レポートテキストの作成に失敗しました'

class ReportWriteFailedError(TasktoryError):
    MSG = 'レポートの作成に失敗しました'

#==============================================================================
# ファイルシステム関連の例外
#==============================================================================
class FSReadTreeFailedError(TasktoryError):
    MSG = 'タスクトリツリーの読み込みに失敗しました'

class FSWriteTreeFailedError(TasktoryError):
    MSG = 'タスクトリツリーの書き込みに失敗しました'

#==============================================================================
# タスクトリ関連の例外
#==============================================================================
class TasktoryMargeFailedError(TasktoryError):
    MSG = 'タスクトリのマージに失敗しました'

class TasktoryOverlapTimetableError(TasktoryError):
    MSG = 'タスクトリツリー中の作業時間に重複があります'

#==============================================================================
# メモ関連の例外
#==============================================================================
class MemoPathNotFoundWarning(TasktoryWarning):
    MSG = 'メモに記載されたパスが見つかりません'

#==============================================================================
# サマリー関連の例外
#==============================================================================
class SummaryHTMLRenderingFailedWarning(TasktoryWarning):
    MSG = 'サマリーHTMLのレンダリングに失敗しました'

#==============================================================================
# その他の例外
#==============================================================================
class UnknownError(TasktoryError):
    MSG = '失敗しました'
