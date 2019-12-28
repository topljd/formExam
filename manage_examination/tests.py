from django.test import TestCase

# Create your tests here.
from django.utils import timezone
from django.test import TestCase

from manage_examination.models import Paper


class TestTest(TestCase):
    def test_timezone(self):
        p=Paper.objects.all()
        print(p)


