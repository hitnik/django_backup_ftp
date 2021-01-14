from django.apps import AppConfig
import django_rq
import datetime
from redis.exceptions import ConnectionError
from django.utils.timezone import pytz
from django.conf import settings

class BackupConfig(AppConfig):
    name = 'backup_ftp'

    def ready(self):
        """
         set datetime in utc for job schedule
        """
        date_now = datetime.datetime.utcnow()
        year = date_now.year
        month = date_now.month
        day = date_now.day
        timezone_local = pytz.timezone(settings.TIME_ZONE)

        date_schedule_dumpdata = datetime.datetime.strptime(settings.DUMPDATA_TIME, '%H:%M:%S')
        hour_dumpdata = date_schedule_dumpdata.hour
        minutes_dumpdata = date_schedule_dumpdata.minute
        seconds_dumpdata = date_schedule_dumpdata.second

        date_schedule_dumpdata = datetime.datetime(year, month, day,
                                                   hour_dumpdata, minutes_dumpdata, seconds_dumpdata)
        date_schedule_dumpdata = timezone_local.localize(date_schedule_dumpdata)
        date_schedule_dumpdata = date_schedule_dumpdata.astimezone(pytz.utc)

        while date_schedule_dumpdata <= datetime.datetime.utcnow().astimezone(pytz.utc):
            date_schedule_dumpdata = date_schedule_dumpdata  + datetime.timedelta(seconds=settings.DUMPDATA_INTERVAL)


        from . import jobs

        try:
            scheduler = django_rq.get_scheduler('default')
            for job in scheduler.get_jobs():
                if job.func_name == 'forumTopics.jobs.dumpdata_ftp':
                    job.delete()

            scheduler.schedule(scheduled_time=date_schedule_dumpdata,
                               func=jobs.dumpdata_ftp,
                               interval=settings.DUMPDATA_INTERVAL, result_ttl=settings.DUMPDATA_INTERVAL+300
                               )

            count_dumpdata = 0
            for job in scheduler.get_jobs():
                if job.func_name == 'forumTopics.jobs.dumpdata_ftp':
                    count_dumpdata += 1
                    if count_dumpdata > 1:
                        job.delete()

            for job in scheduler.get_jobs():
                print(job.func_name)

        except ConnectionError:
            pass