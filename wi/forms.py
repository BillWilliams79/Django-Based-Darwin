from django.forms import ModelForm, Textarea, CharField, TextInput, BooleanField, CheckboxInput, DateTimeInput, DateInput, TimeInput
from .models import task, area
import datetime

#
# create a generic form for a workitem
# 
class taskForm(ModelForm):
    class Meta:
        model = task
        fields = '__all__'

class TaskCreateModelForm(ModelForm):
    class Meta:
        model = task
        fields = ['priority', 'area', 'description', ]
        widgets = {
            'description' : TextInput(attrs={
                                            'class' : 'w-100 text-reset',
                                            }
                                    ),
                }

class TaskUpdateModelForm(ModelForm):
    class Meta:
        model = task
        fields = ['priority', 'status', 'description', 'area', 'created', 'updated' ]
        widgets = {
            'description' : TextInput(attrs={
                                            'class' : 'w-100',
                                            }
                                    ),
        }

class TaskModelFormsetFactoryModelForm(ModelForm):
    class Meta:
        model = task
        fields = ['priority', 'status','area', 'description', 'created',]
        widgets = {
            'description' : TextInput(attrs={
                                            'class' : 'w-100',
                                            }
                                    ),
        }

class TaskInlineFormsetFactoryModelForm(ModelForm):
    class Meta:
        model = task
        fields = ['priority', 'status', 'description', 'created', 'updated' ]
        widgets = {
            'description' : TextInput(attrs={
                                            'class' : 'w-100',
                                            }
            ),
        }

class AreaFocusForm(ModelForm):
    class Meta:
        model = task
        fields = ['priority', 'status', 'description', 'created', 'updated' ]
        widgets = {
            'priority' : CheckboxInput(attrs={'class' : 'darwin_text',}),

            'status' : CheckboxInput(attrs={'class' : 'darwin_text',}),

            'description' : TextInput(attrs={'class' : 'w-100 darwin_text',}),

            #'created' : DateTimeInput(attrs={'class' : 'darwin_text',}, format='%b %d'),
            'created' : DateTimeInput(attrs={'class' : 'darwin_text',}, ),

            #'updated' : DateTimeInput(attrs={'class' : 'darwin_text',}, format='%b %d'),
            'updated' : DateTimeInput(attrs={'class' : 'darwin_text',}, ),
        }

class GardenTaskInlineFormsetFactoryModelForm(ModelForm):
    class Meta:
        model = task
        fields = ['priority', 'status', 'description',]
        widgets = {
            'description' : TextInput(attrs={
                                            'class' : 'w-100',
                                            }
                                    ),
       }


#
# Controlling class for a worksheet.
# Intended for use in interated calls to inline factory
#
class WorkSheetForm(ModelForm):
    class Meta:
        model = task
        fields = ['priority', 'status', 'description',]
        widgets = {
            'description' : TextInput(attrs={
                                            'class' : 'w-100',
                                            }
                                    ),
       }

class AreaMultiEditForm(ModelForm):
    class Meta:
        model = area
        fields = ['name', 'created', 'updated']

class TaskModelForm(ModelForm):
    class Meta:
        model = task
        fields = ['description']

