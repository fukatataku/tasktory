#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import os, datetime, configparser
from multiprocessing import Process, Pipe

import win32api

from lib.core.Tasktory import Tasktory
from lib.core.Manager import Manager
from lib.ui.Journal import Journal
from lib.ui.Report import Report
from lib.ui.TrayIcon import TrayIcon
from lib.monitor.monitor import file_monitor, dir_monitor
from lib.common.RWTemplate import RWTemplate
from lib.common.exceptions import *
from lib.common.common import *

class WinMain:

    BLOCK = 0
    UNBLOCK = 1
    QUIT = 2

    def __init__(self):
        # 日付
        self.today = datetime.date.today()

        # メイン設定読み込み
        self.main_config()

        # システム初期化
        self.initialize()

        # 準備
        self.prepare()

        # トレイアイコンのポップアップメニュー作成
        self.prepare_command()

        # トレイアイコンのポップアップメッセージ作成
        self.prepare_message()

        # サブプロセス準備
        self.prepare_process()
        return

    def main_config(self):
        config = configparser.ConfigParser()
        config.read(MAIN_CONF_FILE, encoding='utf-8-sig')
        self.root = config['MAIN']['ROOT']
        self.profile_name = config['MAIN']['PROFILE_NAME']
        self.memo_name = config['MAIN']['MEMO_NAME']
        self.journal_file = config['JOURNAL']['JOURNAL_FILE']
        self.infinite = int(config['JOURNAL']['INFINITE'])
        self.report_dir = config['REPORT']['REPORT_DIR']
        self.report_name_tmpl = RWTemplate(config['REPORT']['REPORT_NAME'])
        return

    def initialize(self):
        # ルートディレクトリが存在しなければ、作成する
        if not os.path.isfile(os.path.join(self.root, self.profile_name)):
            Manager.put(
                    self.root,
                    Tasktory('', self.today.toordinal()+3650, Tasktory.CONST),
                    self.profile_name)

        # ジャーナルディレクトリが存在しなければ、作成する
        journal_dir = os.path.dirname(self.journal_file)
        if not os.path.isdir(journal_dir):
            os.makedirs(journal_dir)

        return

    def prepare(self):
        # ジャーナルが存在するなら、memoを取り出す
        memo = ''
        if os.path.isfile(self.journal_file):
            _, memo = self.read_journal()

            # タスク固有のメモ部分を捨てる
            memo = Journal.path_reg.split(memo)[0]

        # ファイルシステムからツリーを読み込む
        self.tree = Manager.get_tree(self.root, self.profile_name)

        # 新しいジャーナルを書き出す
        self.write_journal(self.tree, memo)

        # 新しいジャーナルを読み込む
        self.jtree, self.memo = self.read_journal()

        # ファイルシステムの状態を読み込む
        self.paths = Manager.listtask(self.root, self.profile_name)

        return

    def prepare_command(self):
        # メニューコマンドを作成する
        def num():
            n = 0
            while True:
                yield n
                n += 1
            return
        gen = num()
        self.com_map = {}
        self.com_menu = []

        # 同期コマンド
        iD = next(gen)
        self.com_map[iD] = self.sync
        self.com_menu.append(('Sync', iD))

        # レポートコマンド
        sub_menu = []
        iD = next(gen)
        reports = Report.reports()
        self.com_map[iD] = lambda: self.write_report(reports)
        sub_menu.append(('All', iD))
        for name, func in reports:
            iD = next(gen)
            self.com_map[iD] = lambda: self.write_report([(name, func)])
            sub_menu.append((name, iD))
        self.com_menu.append(('Report', sub_menu))

        # セパレータ
        self.com_menu.append((None, None))

        # 終了コマンド
        iD = next(gen)
        self.com_map[iD] = self.quit
        self.com_menu.append(('Quit', iD))

        return

    def prepare_message(self):
        self.popmsg_map = {
                TrayIcon.WP_POPUP_DEBUG : {},
                TrayIcon.WP_POPUP_INFO : {},
                TrayIcon.WP_POPUP_WARN : {},
                TrayIcon.WP_POPUP_ERROR : {},
                TrayIcon.WP_POPUP_FATAL : {},
                }

        # 例外リスト
        classes = ExceptionMeta.classes()
        warnings = [e for e in classes if issubclass(e, TasktoryWarning)]
        errors = [e for e in classes if issubclass(e, TasktoryError)]

        # INFO
        self.popmsg_map[TrayIcon.WP_POPUP_INFO] = INFO_MAP

        # WARNING
        self.popmsg_map[TrayIcon.WP_POPUP_WARN]\
                = dict((cls.ID, cls.MSG) for cls in warnings)

        # ERROR
        self.popmsg_map[TrayIcon.WP_POPUP_ERROR]\
                = dict((cls.ID, cls.MSG) for cls in errors)

        pass

    def prepare_process(self):
        # パイプ
        self.conn = Pipe()

        # トレイアイコン作成／開始
        self.tray_icon = Process(target=TrayIcon,
                args=(self.conn[1], ICON_PATH, self.popmsg_map, self.com_menu))

        # 監視プロセス作成
        self.jnl_monitor = Process(
                target=file_monitor, args=(self.journal_file, self.conn[1]))
        self.fs_monitor = Process(
                target=dir_monitor, args=(self.root, self.conn[1]))

        return

    def read_journal(self):
        # ジャーナル読み込み用のテンプレートを読み込む
        try:
            with open(JOURNAL_READ_TMPL_FILE, 'r', encoding='utf-8-sig') as f:
                journal_tmpl = RWTemplate(f.read())
        except:
            raise JournalReadTemplateReadFailedError()

        # ジャーナル読み込み用のコンフィグを読み込む
        try:
            config = configparser.ConfigParser()
            config.read(JOURNAL_CONF_FILE, encoding='utf-8-sig')
            section = config['ReadTemplate']
            taskline_tmpl = RWTemplate(section['TASKLINE'])
            date_reg = Journal.date_regex(section['DATE'])
            time_reg = Journal.time_regex(section['TIME'])
            times_delim = section['TIMES_DELIM']
        except:
            raise JournalReadConfigReadFailedError()

        # ファイルからジャーナルテキストを読み込む
        if not os.path.isfile(self.journal_file):
            raise JournalFileNotFoundError()
        with open(self.journal_file, 'r', encoding='utf-8-sig') as f:
            journal = f.read()

        # ジャーナルからタスクトリリストを作成する
        try:
            tasktories, memo = Journal.tasktories(
                    journal, journal_tmpl, taskline_tmpl,
                    date_reg, time_reg, times_delim)
        except:
            raise JournalReadFailedError()

        # 同じタスクトリが複数存在する場合は例外を送出する
        paths = [Journal.foot(t).path() for t in tasktories]
        if len(paths) != len(set(paths)):
            raise JournalDuplicateTasktoryError()

        # タスクトリリストを統合してツリーにする
        jtree = sum(tasktories[1:], tasktories[0]) if tasktories else None

        # ツリーを診断する
        if jtree is not None and Manager.overlap(jtree):
            raise JournalOverlapTimetableError()

        return jtree, memo

    def write_journal(self, tree, memo):
        # ジャーナル書き出し用のテンプレートを読み込む
        try:
            with open(JOURNAL_WRITE_TMPL_FILE, 'r', encoding='utf-8-sig') as f:
                journal_tmpl = RWTemplate(f.read())
        except:
            raise JournalWriteTemplateReadFailedError()

        # ジャーナル書き出し用のコンフィグを読み込む
        try:
            config = configparser.ConfigParser()
            config.read(JOURNAL_CONF_FILE, encoding='utf-8-sig')
            section = config['WriteTemplate']
            taskline_tmpl = RWTemplate(section['TASKLINE'])
            date_tmpl = RWTemplate(section['DATE'])
            time_tmpl = RWTemplate(section['TIME'])
            times_delim = section['TIMES_DELIM']
        except:
            raise JournalWriteConfigReadFailedError()

        # ツリーからジャーナルテキストを作成する
        try:
            journal = Journal.journal(
                    self.today, tree, memo, journal_tmpl, taskline_tmpl,
                    time_tmpl, times_delim, self.infinite)
        except:
            raise JournalCreateTextFailedError()

        # ジャーナルテキストをファイルに書き出す
        try:
            with open(self.journal_file, 'w', encoding='utf-8') as f:
                f.write(journal)
        except:
            raise JournalWriteFailedError()

        # ジャーナル読み込みテンプレートを更新する
        try:
            with open(JOURNAL_READ_TMPL_FILE, 'w', encoding='utf-8') as f:
                f.write(journal_tmpl.template)
        except:
            raise JournalReadTemplateUpdateFailedError()

        # ジャーナル読み込みコンフィグを更新する
        try:
            section = config['ReadTemplate']
            section['TASKLINE'] = taskline_tmpl.template.replace('%', '%%')
            section['DATE'] = date_tmpl.template.replace('%', '%%')
            section['TIME'] = time_tmpl.template.replace('%', '%%')
            section['TIMES_DELIM'] = times_delim
            with open(JOURNAL_CONF_FILE, 'w', encoding='utf-8') as f:
                config.write(f)
        except:
            raise JournalReadConfigUpdateFailedError()

        return

    def write_report(self, reports):
        # レポート書き出し開始を通知する
        self.info(INFO_REPO_START)

        # ファイルシステムからタスクツリーを読み込む
        tree = Manager.get_tree(self.root, self.profile_name)

        for name, func in reports:
            # レポートテキストを作成する
            try:
                repo_text = func(self.today, tree)
            except:
                raise ReportCreateTextFailedError()

            # レポートファイルパスを作成する
            repo_filename = self.report_name_tmpl.substitute({
                'YEAR' : str(self.today.year),
                'MONTH' : str(self.today.month),
                'DAY' : str(self.today.day),
                })
            repo_file = os.path.join(self.report_dir, name, repo_filename)

            # ディレクトリが無ければ作成する
            if not os.path.isdir(os.path.join(self.report_dir, name)):
                os.makedirs(os.path.join(self.report_dir, name))

            # ファイルに書き出す
            try:
                with open(repo_file, 'w', encoding='utf-8') as f:
                    f.write(repo_text)
            except:
                raise ReportWriteFailedError()

        # レポート書き出し完了を通知する
        self.info(INFO_REPO_END)
        return

    def update_filesystem(self, force=False):
        # ジャーナルを読み込む
        new_jtree, new_memo = self.read_journal()
        self.memo = new_memo

        # タスクの状態に変化が無ければ無視する
        if Manager.same_tree(self.jtree, new_jtree) and not force:
            return

        # ファイルシステムからツリーを読み出す
        try:
            tree = Manager.get_tree(self.root, self.profile_name)
        except:
            raise FSReadTreeFailedError()

        # 読み出したツリーの内、更新対象タスクの当日の作業時間を抹消する
        start = datetime.datetime.combine(self.today, datetime.time())
        end = start + datetime.timedelta(1)
        start = int(start.timestamp())
        end = int(end.timestamp())
        for node in [tree.find(n.path()) for n in new_jtree]:
            if node is None: continue
            node.timetable = [t for t in node.timetable\
                    if not (start <= t[0] < end)]

        # マージする
        try:
            new_tree = tree + new_jtree
        except:
            TasktoryMargeFailedError()

        # 作業時間の重複の有無を確認する（非必須）
        if Manager.overlap(new_tree):
            raise TasktoryOverlapTimetableError()

        # 未設定項目を補完する
        for node in new_tree:
            # 期日
            if node.deadline is None:
                node.deadline = max([n.deadline for n in node
                    if n.deadline is not None])

            # ステータス
            if node.status is None:
                node.status = Tasktory.OPEN

            # コメント
            if node.comments is None:
                node.comments = ''

        # ファイルシステムへの書き出し開始を通知する
        self.info(INFO_FS_START)

        # ファイルシステムに書き出す
        try:
            for node in new_tree:
                Manager.put(self.root, node, self.profile_name)
        except:
            raise FSWriteTreeFailedError()

        # ファイルシステムへの書き出し完了を通知する
        self.info(INFO_FS_END)

        # メンバ変数にセットする
        self.tree= new_tree
        self.jtree = new_jtree
        return

    def update_memo(self):
        # メモを追記する
        memo_list = Manager.parse_memo(self.memo, Journal.path_reg)
        for path, text in memo_list:
            node = self.tree.find(path)
            if node is None:
                self.warn(MemoPathNotFoundWarning)
                continue
            fullpath = node.path(self.root)
            if Manager.put_memo(
                    datetime.datetime.now(), fullpath, text, self.memo_name):
                self.info(INFO_MEMO_END)
        return

    def update_journal(self, force=False):
        # 現在のファイルシステムの状態を読み込む
        new_paths = Manager.listtask(self.root, self.profile_name)

        # ファイルシステムの状態に変化が無ければ無視する
        if self.paths == new_paths and not force:
            return

        # ファイルシステムからツリーを読み込む
        try:
            tree = Manager.get_tree(self.root, self.profile_name)
        except:
            raise FSReadTreeFailedError()

        # ジャーナルへの書き出し開始を通知する
        self.info(INFO_JNL_START)

        # ジャーナルに書き出す
        self.write_journal(tree, self.memo)

        # ジャーナルへの書き出し完了を通知する
        self.info(INFO_JNL_END)

        # メンバ変数にセットする
        self.paths = new_paths

        return

    def info(self, msg_id):
        win32api.SendMessage(self.hwnd,
                TrayIcon.MSG_POPUP, TrayIcon.WP_POPUP_INFO, msg_id)
        return

    def warn(self, exc):
        win32api.SendMessage(self.hwnd,
                TrayIcon.MSG_POPUP, TrayIcon.WP_POPUP_WARN, exc.ID)
        return

    def error(self, exc):
        win32api.SendMessage(self.hwnd,
                TrayIcon.MSG_POPUP, TrayIcon.WP_POPUP_ERROR, exc.ID)
        return

    def block(self):
        self.conn[1].send((os.getpid(), WinMain.BLOCK))
        return

    def unblock(self):
        self.conn[1].send((os.getpid(), WinMain.UNBLOCK))
        return

    def quit(self):
        self.conn[1].send((os.getpid(), WinMain.QUIT))
        return

    def sync(self):
        # ファイルシステムを更新する
        self.update_filesystem(force=True)

        # ジャーナルを更新する
        self.update_journal(force=True)
        return

    def run(self):
        # プロセス開始
        self.tray_icon.start()
        self.hwnd = self.conn[0].recv()[1]
        self.jnl_monitor.start()
        self.fs_monitor.start()

        try:
            ignore = WinMain.UNBLOCK
            while True:
                # 通知が来るまでブロック
                ret = self.conn[0].recv()

                #==============================================================
                # 自身による通知
                #==============================================================
                if ret[0] == os.getpid():
                    if ret[1] == WinMain.BLOCK:
                        ignore = WinMain.BLOCK
                        continue
                    elif ret[1] == WinMain.UNBLOCK:
                        ignore = WinMain.UNBLOCK
                        continue
                    elif ret[1] == WinMain.QUIT:
                        break

                # 自分自身による更新は無視する
                elif ignore == WinMain.BLOCK:
                    continue

                #==============================================================
                # ジャーナルが更新された場合の処理
                #==============================================================
                if ret[0] == self.jnl_monitor.pid:
                    self.block()
                    try:
                        self.update_filesystem()
                        self.update_memo()
                    except TasktoryError as e:
                        self.error(e)
                        continue
                    finally:
                        self.unblock()

                #==============================================================
                # ファイルシステムが更新された場合の処理
                #==============================================================
                elif ret[0] == self.fs_monitor.pid:
                    self.block()
                    try:
                        self.update_journal()
                    except TasktoryError as e:
                        self.error(e)
                        continue
                    finally:
                        self.unblock()

                #==============================================================
                # トレイアイコンからコマンドが実行された場合の処理
                #==============================================================
                elif ret[0] == self.tray_icon.pid:
                    self.block()
                    try:
                        self.com_map[ret[1]]()
                    except TasktoryError as e:
                        self.error(e)
                        continue
                    finally:
                        self.unblock()
        finally:
            win32api.SendMessage(self.hwnd, TrayIcon.MSG_DESTROY, None, None)
            self.tray_icon.terminate()
            self.jnl_monitor.terminate()
            self.fs_monitor.terminate()
            for conn in self.conn: conn.close()
        return

if __name__ == '__main__':
    main = WinMain()
    main.run()
