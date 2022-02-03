from django.db import models
#from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.conf import settings
#from django import utils
# Create your models here.

class task(models.Model):

    priority = models.BooleanField(
                '!',
                default = False, 
                null = False,
                blank = False,
    )

    status = models.BooleanField(
                'Done',
                default = False, 
                null = False,
                blank = False,
    )

    description = models.CharField(
                max_length=100,
                null = False,
                blank = False,
    )

    area = models.ForeignKey(
                'area',
                on_delete=models.SET_NULL,
                null = True,
    )

    created_by = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.SET_NULL,
                null = True,
    )

    created = models.DateTimeField(
                null = True,
                blank = True,
                editable = True,
    )
 
    updated = models.DateTimeField(
                null = True,
                blank = True,
    )
 
    def save(self, *args, **kwargs):
        #
        # intercept all saves and process time updates.
        #   -> used to be done with auto_now and auto_now_add. but these forced editable to be fals
        #   -> so items were not displayed in factories and the admin
        # Case1 - newly created items won't have an id to save. updated created
        # Case2 - always set updated to current time
        #
        if not self.id:
            self.created = timezone.now()
        
        self.updated = timezone.now()
        
        return super(task, self).save(*args, **kwargs)

    def __str__(self):
        #
        # description is always the best for task's smallest representation
        #
        return(f"{self.description}")

class area(models.Model):

    name = models.CharField(
                max_length=25,
#                help_text = 'Brief description of task',
                null = False,
                blank = False,
    )

    created = models.DateTimeField(
                null = True,
                blank = True,
                editable = True,
    )
 
    updated = models.DateTimeField(
                null = True,
                blank = True,
    )

    def save(self, *args, **kwargs):
        #
        # intercept all saves and process time updates.
        #   -> used to be done with auto_now and auto_now_add. but these forced editable to be fals
        #   -> so items were not displayed in factories and the admin
        # Case1 - newly created items won't have an id to save. updated created
        # Case2 - always set updated to current time
        #
        if not self.id:
            self.created = timezone.now()
        
        self.updated = timezone.now()
        
        return super(area, self).save(*args, **kwargs)

    def __str__(self):
        return(f"{self.name}")