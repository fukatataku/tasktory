#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import win32serviceutil
import win32file
import win32con

ACTIONS = {
        1 : "Created",
        2 : "Deleted",
        3 : "Updated",
        4 : "Renamed from Something",
        5 : "Renamed to Something"
        }
FILE_LIST_DIRECTORY = 0x0001

class JournalMonitor(win32serviceutil.ServiceFramework):

    PATH = None

    @classmethod
    def set_path(path):
        cls.PATH = path

    def __init__(self, args):
        super().__init__(self, args)

        # 監視するディレクトリのハンドルを取得する
        SHARE_FLAG = win32con.FILE_SHARE_READ |\
                win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE
        self.hDir = win32file.CreateFile(
                self.PATH, 0x0001, SHARE_FLAG, None, win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS, None)

        # 監視するアクション
        self.NOTIFY_FLAG = win32con.FILE_NOTIFY_CHANGE_DIR_NAME

    def SvcDoRun(self):
        while True:
            # 監視対象が変更されるまで待機
            results = win32file.ReadDirectoryChangesW(
                    self.hDir, 1024, True, self.NOTIFY_FLAG, None, None)

            # TODO: 変更内容を調べる
        return

    def SvcStop(self):
        return

