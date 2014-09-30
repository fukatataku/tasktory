#-*- encoding:utf-8 -*-

from lib.service.monitor.JournalMonitor import JournalMonitor

if __name__ == '__main__':
    JournalMonitor.add_monitor('C:/home/fukata/management/journal', lambda t:t)
    JournalMonitor.add_monitor('C:/home/fukata/work', lambda t:t)

    # サービスに登録
    win32serviceutil.HandleCommandLine(JournalMonitor)
