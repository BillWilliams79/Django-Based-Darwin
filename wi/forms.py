from django.forms import ModelForm, TextInput, CheckboxInput, ModelChoiceField, Textarea
from .models import domain, area, task


#
# Tasks Display Form
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
            'priority' : CheckboxInput(attrs={'class' : 'darwin_text',}),

            'status' : CheckboxInput(attrs={'class' : 'darwin_text',}),

            'description' : TextInput(attrs={'class' : 'w-100 darwin_text',}),
 #           'description' : Textarea(attrs={'class' : 'w-100 darwin_text',}),

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
        fields = ['name', 'retain_completed_tasks', 'created', 'updated']
