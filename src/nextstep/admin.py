from django.contrib import admin

from nextstep import models

# Register your models here.

admin.site.register(models.Tag)
admin.site.register(models.Application)
admin.site.register(models.ApplicationTag)
admin.site.register(models.UserEmailAccount)
