from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    colour = models.CharField(max_length=8, null=False, default="3B82F6")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
        null=True,
    )

    def __str__(self):
        return self.name


class Application(models.Model):
    role = models.CharField(null=False, blank=False)
    role_link = models.CharField(null=False, blank=True)

    company = models.CharField(null=False, blank=False)
    company_link = models.CharField(null=False, blank=True)

    applied_timestamp = models.DateTimeField(null=False, default=timezone.now)

    job_description = models.TextField(null=False, blank=True)

    tags = models.ManyToManyField(Tag, through="ApplicationTag", related_name="tags")

    def get_current_tag(self) -> Tag | None:
        tags = ApplicationTag.objects.filter(application=self).order_by("-updated_at")

        return tags.first().tag

    def get_all_tags(self) -> QuerySet["ApplicationTag"]:
        return ApplicationTag.objects.filter(application=self)


class ApplicationTag(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    # auto_now updates the field every time the save() method is called
    updated_at = models.DateTimeField(auto_now=True)


class EmailIntegration(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_integration",
    )
