from django.contrib import admin
from .models import domain, area, task

# Register your models here.
admin.site.register(domain)
admin.site.register(area)
admin.site.register(task)
