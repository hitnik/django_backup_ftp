from django_rq import job
from .management.commands.dumpdata_ftp import Command as DumpCommand


@job
def dumpdata_ftp():
    try:
        dump =DumpCommand()
        dump.handle()
    except:
        pass