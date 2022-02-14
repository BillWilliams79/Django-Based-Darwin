from django.forms import ModelForm, TextInput, CheckboxInput, ModelChoiceField
from .models import domain, area, task
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
        # example setting html label, help text and error messages in a form
        # of couse the helptext is not displayed because the template doesn't render it
        labels = {
            'area': ('Task Area'),
        }
        help_texts = {
            'area': ('Logical grouping of your tasks'),
        }
        error_messages = {
            'description': {
                'max_length': ("Task descriptions should be very brief, hence limited to 100 characters"),
            },
        }
        # example using widgets to set HTML attributes and (potentially) override the the 
        # default django widget for your model field.
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

    #
    # placing area here allows us to override its query set in the view code
    # to limit based on created_by
    #     
    area = ModelChoiceField(queryset = area.objects.all())
    
    class Meta:
        model = task
        fields = ['priority', 'status', 'area', 'description', ]
        widgets = {
            'priority' : CheckboxInput(attrs={'class' : 'darwin_text',}),

            'status' : CheckboxInput(attrs={'class' : 'darwin_text',}),

            'description' : TextInput(attrs={'class' : 'w-100 darwin_text',}),

            #'created' : DateTimeInput(attrs={'class' : 'darwin_text',}, format='%b %d'),

            #'updated' : DateTimeInput(attrs={'class' : 'darwin_text',}, format='%b %d'),
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

    domain = ModelChoiceField(queryset = area.objects.all())

    class Meta:
        model = area
        fields = ['name', 'domain', 'created', 'updated']


class DomainMultiEditForm(ModelForm):
    class Meta:
        model = domain
        fields = ['name', 'retain_completed_tasks', 'created', 'updated']

class TaskModelForm(ModelForm):
    class Meta:
        model = task
        fields = ['description']

