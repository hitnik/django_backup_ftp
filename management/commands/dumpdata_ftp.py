from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings
import sys
import os
import datetime
from backup_ftp.utils import archive_file
from backup_ftp.ftp import FTP_backup
import re


class Command(BaseCommand):

    def handle(self, *args, **options):
        BASE_DIR = os.path.abspath(os.path.dirname(__name__))
        FTP_HOST = settings.FTP_BACKUP_HOST
        FTP_PORT = settings.FTP_BACKUP_PORT
        FTP_USER = settings.FTP_BACKUP_USER
        FTP_PASSWORD = settings.FTP_BACKUP_PASSWORD
        FTP_FILES_COUNT = settings.FTP_BACKUP_FILES_COUNT
        FTP_USE_TLS = settings.FTP_BACKUP_USE_TLS
        FTP_DIR = settings.FTP_DIR

        path = os.path.join(BASE_DIR, 'backups')

        if not os.path.exists(path):
            os.mkdir(path, 0o755)

        date = datetime.datetime.now()
        file = 'fulldump' + date.strftime('%Y%m%d%H%M') +'.json'
        json_src = os.path.join(path, file)

        with open(json_src, 'w') as f:
            management.call_command('dumpdata', indent=2, stdout=f)

        archive_path = archive_file(json_src)

        ftp = FTP_backup(host=FTP_HOST, port=FTP_PORT, use_tls=FTP_USE_TLS)
        if ftp.connect(timeout=10) and ftp.login(user=FTP_USER, password=FTP_PASSWORD):
            ftp.open_dir(FTP_DIR)
            ftp.upload_file(archive_path)
            files_list = ftp.list_files()
            if len(files_list) > FTP_FILES_COUNT:
                for index, item in enumerate(files_list):
                    file_attrs = re.split(r'\s+', item)
                    date_str = file_attrs[0] + ' ' + file_attrs[1]
                    file_name = file_attrs[-1]
                    date = datetime.datetime.strptime(date_str, '%m-%d-%y %I:%M%p')
                    file_attrs = {'date': date, 'file': file_name}
                    files_list[index] = file_attrs
                files_list = sorted(files_list, key = lambda i: i['date'], reverse=True)
                for item in files_list[FTP_FILES_COUNT:]:
                    ftp.delete_file(item['file'])
        ftp.quit()
        if os.path.exists(json_src):
            os.remove(json_src)
        if os.path.exists(archive_path):
            os.remove(archive_path)




