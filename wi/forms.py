from django.forms import ModelForm, TextInput, CheckboxInput, ModelChoiceField, Textarea, DateTimeField, DateTimeInput
from django import forms
from .models import domain, area, task

#
# Tasks Display Form
#
class WorkSheetForm(ModelForm):
    #status = forms.BooleanField(label = 'Done', label_suffix = '', )
    #description = forms.CharField(label_suffix = '', )

    class Meta:
        model = task
        fields = ['priority', 'status', 'description',]
        widgets = {
            'priority' : CheckboxInput(attrs={'class': 'task-priority',}),
            'status' : CheckboxInput(attrs={'class': 'task-status',}),
            'description' : Textarea(attrs={'class' : 'task-description w-100 p-0 me-1 border-0',}),
                    }

#
# Area Focus Form
#
class AreaFocusForm(ModelForm):
    #
    # placing area here allows us to override its query set in the view code
    # to limit based on created_by field
    #     
    area = ModelChoiceField(queryset = area.objects.all())
    #
    # for this form, display the completed field but show only the date.
    # This is the best examplar to date to override the model field definitions.
    #
    completed = DateTimeField(input_formats=['%b %d, %Y %H:%M:%S'],
                                required=False,
                                widget = DateTimeInput(
                                                format = '%b %d, %Y %H:%M:%S',
                                                attrs = {'size':'14',
                                                         'class': 'task-completed',}))

    class Meta:
        model = task
        fields = ['priority', 'status', 'description', 'completed' ]
        widgets = {
           # 'priority' : CheckboxInput(attrs={'class': 'darwin_text',}),

            'status' : CheckboxInput(attrs={'class' : 'task-status',}),

            'description' : Textarea(attrs={'class' : 'task-description p-0 border-0',}),
 
        }

#
# Area Editor Form
#
class AreaMultiEditForm(ModelForm):

    domain = ModelChoiceField(queryset = area.objects.all())

    class Meta:
        model = area
        fields = ['name', 'domain', 'hide',]

#
# Domain Editor Form
#
class DomainMultiEditForm(ModelForm):
    class Meta:
        model = domain
        fields = ['name', 'retain_completed_tasks', ]
