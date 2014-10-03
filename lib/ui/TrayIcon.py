# -*- encoding:utf-8 -*-

import win32api, win32gui, win32con

class TrayIcon:

    import win32api, win32gui, win32con

    ICON_PATH = 'C:/home/fukata/git/tasktory/sample/py.ico'
    MSG_NOTIFY = win32con.WM_USER + 20
    MSG_POPUP = win32con.WM_USER + 21

    def __init__(self, conn):
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
        conn.send(self.hwnd)

        # アイコンを作成する
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        self.hicon = win32gui.LoadImage(hinst, self.ICON_PATH,
                win32con.IMAGE_ICON, 0, 0, icon_flags)

        # タスクバーにアイコンを追加する
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, self.MSG_NOTIFY, self.hicon, 'HOGE')
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

        self.run()
        return

    def run(self):
        win32gui.PumpMessages()
        return

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
            self.menu()
        elif lparam == win32con.WM_RBUTTONDOWN:
            pass
        elif lparam == win32con.WM_RBUTTONDBLCLK:
            pass
        return

    def popup(self, hwnd, msg, wparam, lparam):
        title = 'TITLE'
        msg = 'MESSAGE'
        nid = (self.hwnd, 0, win32gui.NIF_INFO, self.MSG_NOTIFY,
                self.hicon, 'INFOMATION', msg, 200, title)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
        return

    def menu(self):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1024, 'Quit')
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1],
                0, self.hwnd, None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1

if __name__ == '__main__':
    from multiprocessing import Process, Pipe
    import time
    conn1, conn2 = Pipe()
    msg = TrayIcon.MSG_POPUP
    p = Process(target=TrayIcon, args=(conn2,))
    p.start()
    hwnd = conn1.recv()
    conn1.close()
    conn2.close()

    time.sleep(5)
    win32api.SendMessage(hwnd, msg, None, None)
    #time.sleep(10)
    #win32api.SendMessage(hwnd, msg, None, None)
    #time.sleep(10)

    p.join()
    pass
