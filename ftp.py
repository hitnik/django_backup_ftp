from ftplib import FTP_TLS, FTP, error_perm
from socket import timeout as TimeOutError
import re
import os


class FTP_backup():

    def __init__(self, host, port=21, use_tls=False):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        if use_tls:
            self.ftp = FTP_TLS()
        else:
            self.ftp = FTP()

    def connect(self, timeout=None):
        try:
            con = self.ftp.connect(host=self.host, port=self.port, timeout=timeout)
            if re.match(r'220', con):
                return True
        except (TimeOutError, ConnectionRefusedError) as e:
            return False
        return False

    def login(self, user='anonymous', password=None):
        try:
            self.ftp.login(user=user, passwd=password)
            return True
        except error_perm:
            return False
        return False

    def quit(self):
        self.ftp.quit()

    def open_dir(self, dirname):
        self.ftp.cwd(dirname)

    def list_files(self):
        data = []
        self.ftp.dir(data.append)
        return data

    def download_file(self, file_name, path_to):
        out = os.path.join(path_to, file_name)
        with open(out, 'wb') as file:
            self.ftp.retrbinary('RETR ' + file_name, file.write)
        return out

    def upload_file(self, path):
        head, tail = os.path.split(path)
        file = open(path, 'rb')
        self.ftp.storbinary('STOR ' + tail, file, 1024)
        file.close()
        return tail

    def delete_file(self, file):
        self.ftp.delete(file)
        return file

if __name__ == '__main__':
    ftp = FTP_backup(host='10.254.90.22', port=21, use_tls=True)
    print(ftp.connect())
    print(ftp.login(user='omc', password='center'))
    # ftp.open_dir('backups')
    # print(ftp.list_files())
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # path = os.path.join(BASE_DIR, 'backup_ftp')
    # ftp.download_file('test.txt', path)
    # out = os.path.join(path, 'test_upload.txt')
    # print(out)
    # ftp.upload_file(out, 'TXT')
    # print(BASE_DIR)
    # print(ftp.delete_file('test_upload.tar'))
    ftp.quit()
