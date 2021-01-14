from django.test import TestCase
from django_rq import get_queue
from .jobs import dumpdata_ftp
# Create your tests here.

class TestJobs(TestCase):

    def testdump(self):
        queue = get_queue('default')
        queue.enqueue(dumpdata_ftp)

