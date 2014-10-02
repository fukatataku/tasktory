# -*- encoding:utf-8 -*-

def monitor(dirpath, conn):
    """targetが示すディレクトリに変更があったら、その変更内容をconnにsendする
    プロセスを作成して通信用のパイプの片方を渡して使用する
    """
    import win32file, win32con

    SHARE_FLAG = win32con.FILE_SHARE_READ |\
            win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE

    # 監視する変更内容
    NOTIFY_FLAG = win32con.FILE_NOTIFY_CHANGE_FILE_NAME |\
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |\
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |\
            win32con.FILE_NOTIFY_CHANGE_SIZE |\
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |\
            win32con.FILE_NOTIFY_CHANGE_SECURITY

    # 監視するディレクトリのハンドルを取得する
    hDir = win32file.CreateFile(dirpath, 0x0001, SHARE_FLAG, None,
            win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None)

    while True:
        # ディレクトリに変更があるまでブロックする
        ret = win32file.ReadDirectoryChangesW(
                hDir, 2014, True, NOTIFY_FLAG, None, None)

        # 変更内容を送信する
        conn.send(ret)
    return
