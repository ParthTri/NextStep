from django.test import TestCase
from django.utils import timezone

from nextstep import models


class TestApplication(TestCase):
    def test_instance(self):
        application = models.Application.objects.create(
            role="Junior Developer",
            company="Pied Piper",
        )

        self.assertTrue(isinstance(application, models.Application))

        # Test value
        self.assertEquals(application.role, "Junior Developer")

        # Making sure autoformated date is working
        self.assertEquals(
            application.applied_timestamp.strftime("%d-%m-%Y"),
            timezone.now().strftime("%d-%m-%Y"),
        )

        # Make sure default values for links are blank links
        self.assertEquals(application.role_link, "")
        self.assertEquals(application.company_link, "")
        self.assertEquals(application.job_description, "")
