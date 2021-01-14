from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings
import os
from backup_ftp.utils import extract_file
from backup_ftp.ftp import FTP_backup
import re

class Command(BaseCommand):

    def handle(self, *args, **options):
        BASE_DIR = os.path.abspath(os.path.dirname(__name__))
        FTP_HOST = settings.FTP_BACKUP_HOST
        FTP_PORT = settings.FTP_BACKUP_PORT
        FTP_USER = settings.FTP_BACKUP_USER
        FTP_PASSWORD = settings.FTP_BACKUP_PASSWORD
        FTP_USE_TLS = settings.FTP_BACKUP_USE_TLS
        FTP_DIR = settings.FTP_DIR

        app_path = os.path.join(BASE_DIR, 'backup_ftp')

        path = os.path.join(app_path, 'fixtures')

        if not os.path.exists(path):
            os.mkdir(path, 0o755)

        ftp = FTP_backup(host=FTP_HOST, port=FTP_PORT, use_tls=FTP_USE_TLS)
        if ftp.connect(timeout=10) and ftp.login(user=FTP_USER, password=FTP_PASSWORD):
            ftp.open_dir(FTP_DIR)
            files_list = ftp.list_files()
            for index, item in enumerate(files_list):
                file_attrs = re.split(r'\s+', item)
                file_name = file_attrs[-1]
                files_list[index] = file_name

            print("Input digit of which file you want to restore. 0 to cancel")

            while True:
                print('Available dump files')
                for index, item in enumerate(files_list):
                    print(f'[{index + 1}] ---  {item}')
                print('----------')
                try:
                    i = int(input())
                    if i > 0 and i <= len(files_list):
                        i -= 1
                        break
                    elif i == 0:
                        return
                    print('!!!Wrong input, Repeat')
                    print()
                except ValueError:
                    print('!!!Wrong input. Digits only')
            tar_path = ftp.download_file(files_list[i], path)
            json_path = extract_file(tar_path)

        ftp.quit()
        if os.path.exists(tar_path):
            os.remove(tar_path)
        management.call_command('loaddata', json_path)

