from django.forms import ModelForm, TextInput, CheckboxInput, ModelChoiceField, Textarea
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
            'description' : Textarea(attrs={'class' : 'task-description w-100 p-0 flex-fill border-0',}),
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
    
    class Meta:
        model = task
        fields = ['priority', 'status', 'description', 'area', 'completed' ]
        widgets = {
            'priority' : CheckboxInput(attrs={'class': 'darwin_text',}),

            'status' : CheckboxInput(attrs={'class' : 'darwin_text',}),

            'description' : TextInput(attrs={'class' : 'w-100, darwin_text',}),
 
        }

#
# Area Editor Form
#
class AreaMultiEditForm(ModelForm):

    domain = ModelChoiceField(queryset = area.objects.all())

    class Meta:
        model = area
        fields = ['name', 'domain', 'hide', 'created', 'updated']

#
# Domain Editor Form
#
class DomainMultiEditForm(ModelForm):
    class Meta:
        model = domain
        fields = ['name', 'retain_completed_tasks', ]
