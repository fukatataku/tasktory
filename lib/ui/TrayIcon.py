#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import os
import win32api, win32gui, win32con

class TrayIcon:

    MSG_NOTIFY = win32con.WM_USER + 20
    MSG_POPUP = win32con.WM_USER + 21
    MSG_DESTROY = win32con.WM_USER + 22

    def __init__(self, conn, icon_path, popmsg_map, com_menu):
        # 引数をメンバ変数に格納する
        self.conn = conn
        self.popmsg_map = popmsg_map
        self.com_menu = com_menu

        # ウィンドウプロシージャを作成する
        message_map = {
                win32con.WM_DESTROY: self.destroy,
                win32con.WM_COMMAND: self.command,
                self.MSG_NOTIFY: self.notify,
                self.MSG_POPUP: self.popup,
                self.MSG_DESTROY: self.start_destroy,
                }

        # ウィンドウクラスを作成する
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = 'TasktoryTrayIcon'
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map

        # ウィンドウクラスを登録する
        classAtom = win32gui.RegisterClass(wc)

        # ウィンドウを作成する
        title = ''
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(wc.lpszClassName, title, style,
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)

        # 親プロセスにウィンドウハンドルを渡す
        self.conn.send((os.getpid(), self.hwnd))

        # アイコンを作成する
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        self.hicon = win32gui.LoadImage(hinst, icon_path,
                win32con.IMAGE_ICON, 0, 0, icon_flags)

        # タスクバーにアイコンを追加する
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, self.MSG_NOTIFY, self.hicon, 'Tasktory')
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

        # ポップアップメニューを作成する
        self.menu = win32gui.CreatePopupMenu()
        for text, item in self.com_menu:
            self.menu = TrayIcon.create_menu(self.menu, item, text)

        # メッセージループに入る
        win32gui.PumpMessages()

    def start_destroy(self, hwnd, msg, wparam, lparam):
        win32gui.DestroyWindow(hwnd)
        return

    def destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)
        return

    def command(self, hwnd, msg, wparam, lparam):
        self.conn.send((os.getpid(), wparam))
        return

    def notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONUP:
            pass
        if lparam == win32con.WM_LBUTTONDOWN:
            pass
        elif lparam == win32con.WM_LBUTTONDBLCLK:
            pass
        elif lparam == win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam == win32con.WM_RBUTTONDOWN:
            pass
        elif lparam == win32con.WM_RBUTTONDBLCLK:
            pass
        return

    def popup(self, hwnd, msg, wparam, lparam):
        title = self.popmsg_map[wparam][0]
        msg = self.popmsg_map[wparam][1]
        nid = (self.hwnd, 0, win32gui.NIF_INFO, self.MSG_NOTIFY,
                self.hicon, 'INFOMATION', msg, 200, title)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
        return

    def show_menu(self):
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(self.menu, win32con.TPM_LEFTALIGN,
                pos[0], pos[1], 0, self.hwnd, None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1

    @staticmethod
    def create_menu(menu, item, text):
        # 通常のメニューアイテム
        if isinstance(item, int):
            flag = win32con.MF_STRING

        # サブメニュー
        elif isinstance(item, list):
            flag = win32con.MF_POPUP
            sub_menu = win32gui.CreatePopupMenu()
            for s,v in item:
                sub_menu = TrayIcon.create_menu(sub_menu, v, s)
            item = sub_menu

        # セパレータ
        elif item is None:
            flag = win32con.MF_SEPARATOR
            item = 0
            text = ''

        win32gui.AppendMenu(menu, flag, item, text)
        return menu

if __name__ == '__main__':
    from multiprocessing import Process, Pipe
    import os, time

    # アイコンのパス
    icon_path = 'C:/home/fukata/dev/tasktory/resource/tasktory.ico'
    # ポップアップメッセージ
    popmsg_map = {
            0 : ('ジャーナルエラー', '作業時間の重複'),
            1 : ('ジャーナルエラー', '同名のタスクトリ'),
            2 : ('ジャーナル更新', 'ファイルシステムに書き出し開始'),
            3 : ('ジャーナル更新', 'ファイルシステムに書き出し完了'),
            4 : ('ファイルシステム更新', 'ジャーナルに書き出し開始'),
            5 : ('ファイルシステム更新', 'ジャーナルに書き出し完了'),
            }
    # レポート
    com_menu = [
            ('Sync', 0),
            ('Report', [
                ('ALL', 1),
                ('チーム週報', 2),
                ('チーム月報', 3),
                ]),
            (None, None),
            ('Quit', 4),
            ]

    conn1, conn2 = Pipe()
    p = Process(target=TrayIcon, args=(conn2, icon_path, popmsg_map, com_menu))
    p.start()
    hwnd = conn1.recv()[1]

    while True:
        ret = conn1.recv()
        print(ret)
        if ret[1] == 4:
            print('終了します')
            win32api.SendMessage(hwnd, TrayIcon.MSG_DESTROY, None, None)
            break

    p.join()
    conn1.close()
    conn2.close()
    pass
