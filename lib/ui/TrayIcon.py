# -*- encoding:utf-8 -*-

import win32api, win32gui, win32con

class TrayIcon:

    MSG_NOTIFY = win32con.WM_USER + 20
    MSG_POPUP = win32con.WM_USER + 21

    def __init__(self, conn, icon_path, popmsg_map, repo_map):
        # 引数をメンバ変数に格納する
        self.conn = conn
        self.popmsg_map = popmsg_map
        self.repo_map = repo_map

        # ウィンドウプロシージャを作成する
        message_map = {
                win32con.WM_DESTROY: self.destroy,
                win32con.WM_COMMAND: self.command,
                self.MSG_NOTIFY: self.notify,
                self.MSG_POPUP: self.popup,
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
        self.conn.send(self.hwnd)

        # アイコンを作成する
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        self.hicon = win32gui.LoadImage(hinst, self.icon_path,
                win32con.IMAGE_ICON, 0, 0, icon_flags)

        # タスクバーにアイコンを追加する
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, self.MSG_NOTIFY, self.hicon, 'Tasktory')
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

        # TODO: ポップアップメニューを作成する
        self.menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(self.menu, win32con.MF_STRING, 1024, 'Quit')

        # メッセージループに入る
        win32gui.PumpMessages()

    def restart(self, hwnd, msg, wparam, lparam):
        return

    def destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)
        return

    def command(self, hwnd, msg, wparam, lparam):
        par = win32api.LOWORD(wparam)
        if par == 1024:
            win32gui.DestroyWindow(self.hwnd)
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
        win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1],
                0, self.hwnd, None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1

if __name__ == '__main__':
    from multiprocessing import Process, Pipe
    import time

    # アイコンのパス
    icon_path = '/Users/taku/git/tasktory/resource/py.ico'
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
    repo_map = {
            0 : 'all',
            1 : 'チーム日報',
            2 : 'チーム週報',
            3 : '会社月報',
            }

    conn1, conn2 = Pipe()
    p = Process(target=TrayIcon, args=(conn2, icon_path, popmsg_map, repo_map))
    p.start()
    hwnd = conn1.recv()

    time.sleep(5)
    win32api.SendMessage(hwnd, 0, None, None)

    p.join()
    conn1.close()
    conn2.close()
    pass
