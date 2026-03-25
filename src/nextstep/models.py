from django.db import models
from django.utils import timezone

# Create your models here.


class Application(models.Model):
    role = models.CharField(null=False, blank=False)
    role_link = models.CharField(null=False, blank=True)

    company = models.CharField(null=False, blank=False)
    company_link = models.CharField(null=False, blank=True)

    applied_timestamp = models.DateTimeField(null=False, default=timezone.now)

    job_description = models.TextField(null=False, blank=True)
