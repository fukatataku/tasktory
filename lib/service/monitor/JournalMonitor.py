# -*- encoding:utf-8 -*-

from multiprocessing import Process, Pipe
import win32service, win32serviceutil
import win32event, win32file, win32con

class JournalMonitor(win32serviceutil.ServiceFramework):

    _svc_name_ = 'JournalMonitor'
    _svc_display_name_ = 'Journal Monitor'
    _svc_description_ = 'Tasktory monitoring service'

    MONITOR = []

    def __init__(self, *args):
        super().__init__(*args)

        # パイプを作成する
        self.parent_conn, self.child_conn = Pipe()

        # プロセスリストを初期化する
        self.processes = []

    def SvcDoRun(self):
        # 子プロセスを作成する
        self.processes = [Process(target=f, args=(p, child_conn))
                for p,f in self.MONITOR]

        # 子プロセスを開始する
        for p in self.processes: p.start()

        while True:
            try:
                # 子プロセスから通知があるまで待機する
                ret = self.parent_conn.recv()

                # TODO: 通知を受けて処理を行う

            except EOFError as e:
                # 子プロセス側のパイプクローズにより終了処理を行う
                self.parent_conn.close()
                for p in self.processes: p.join()
                break
        return

    def SvcStop(self):
        # 終了を通知する
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # 子プロセス側のパイプをクローズし、Pipe.recv()を強制終了する
        self.child_conn.close()

        # 子プロセスを終了する
        for p in self.processes: p.terminate()
        return

    @classmethod
    def add_monitor(cls, dirpath, monitor_func):
        cls.MONITOR.append((dirpath, monitor_func))

def monitor(dirpath, conn):
    SHARE_FLAG = win32con.FILE_SHARE_READ |\
            win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE
    NOTIFY_FLAG = win32con.FILE_NOTIFY_CHANGE_FILE_NAME |\
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |\
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |\
            win32con.FILE_NOTIFY_CHANGE_SIZE |\
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |\
            win32con.FILE_NOTIFY_CHANGE_SECURITY

    # 監視するディレクトリへのハンドルを取得する
    hDir = win32file.CreateFile(dirpath, 0x0001, SHARE_FLAG, None,
            win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None)

    while True:
        # ディレクトリに変更があるまで待機する
        ret = win32file.ReadDirectoryChangesW(hDir, 1024, True,
                NOTIFY_FLAG, None, None)

        # 変更内容をパイプで送信する
        for action, filename in ret:
            conn.send("{0} {1}.".format(os.path.join(dirpath, filename),
                ACTIONS[action]))
    return
