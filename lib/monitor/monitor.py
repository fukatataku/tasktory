# -*- encoding:utf-8 -*-

def dir_monitor(dirpath, conn, monitor_id):
    """指定したディレクトリとそこに含まれるディレクトリに変更があったら通知する
    """
    import os, win32file, win32con

    # 共有フラグ
    SHARE_FLAG = win32con.FILE_SHARE_READ |\
            win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE

    # 監視する変更内容
    NOTIFY_FLAG = win32con.FILE_NOTIFY_CHANGE_DIR_NAME

    # 監視するディレクトリのハンドルを取得する
    hDir = win32file.CreateFile(dirpath, 0x0001, SHARE_FLAG, None,
            win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None)

    while True:
        # ディレクトリに変更があるまでブロックする
        ret = win32file.ReadDirectoryChangesW(
                hDir, 2014, True, NOTIFY_FLAG, None, None)

        # 通知する
        conn.send(monitor_id)
    return

def file_monitor(filepath, conn, monitor_id):
    """指定したファイルに変更があったら通知する。
    """
    import os, win32file, win32con

    # ディレクトリパスとファイル名を取得する
    dirpath = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    # 共有フラグ
    SHARE_FLAG = win32con.FILE_SHARE_READ |\
            win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE

    # 監視する変更内容
    NOTIFY_FLAG = win32con.FILE_NOTIFY_CHANGE_FILE_NAME |\
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE

    # 監視するディレクトリのハンドルを取得する
    hDir = win32file.CreateFile(dirpath, 0x0001, SHARE_FLAG, None,
            win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None)

    while True:
        # ディレクトリに変更があるまでブロックする
        ret = win32file.ReadDirectoryChangesW(
                hDir, 2014, True, NOTIFY_FLAG, None, None)

        # 変更内容を確認して通知する
        for act, path in ret:
            # 対象ファイルでなければ無視する
            if path != filename: continue

            # 通知する
            conn.send(monitor_id)
    return
