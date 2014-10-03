#!C:/python/python3.4/python
# -*- encoding:utf-8 -*-

import win32api
import win32gui
import win32con
import sys, os
import struct
import time

class BalloonTip:
    def __init__(self, title, msg):
        message_map = {win32con.WM_DESTROY: self.OnDestroy}

        # Register the Window class
        wc = win32gui.WNDCLASS()
        hInst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = 'PythonTaskbar'
        wc.lpfnWndProc = message_map
        classAtom = win32gui.RegisterClass(wc)

        # Create the Window
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hWnd = win32gui.CreateWindow(classAtom, 'Taskbar', style,
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                0, 0, hInst, None)
        win32gui.UpdateWindow(self.hWnd)

        # Icon
        iconPathName = os.path.abspath(
                os.path.join(sys.path[0], 'balloontip.ico'))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            hIcon = win32gui.LoadImage(hInst, iconPathName,
                    win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hWnd, 0, flags, win32con.WM_USER+20, hIcon, 'tooltip')
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                (self.hWnd, 0, win32gui.NIF_INFO, win32con.WM_USER+20,
                    hIcon, 'Balloon tooltip', msg, 200, title))

        # Block
        time.sleep(10)
        win32gui.DestroyWindow(self.hWnd)

    def OnDestroy(self, hWnd, msg, wparam, lparam):
        nid = (self.hWnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)
        return

def balloon(title, msg):
    w = BalloonTip(title, msg)

if __name__ == '__main__':
    #balloon_tip("Title for popup", "This is the popup's message")
    balloon = BalloonTip('TITLE', 'MSG')
