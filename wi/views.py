from django.views.generic import ListView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse, reverse_lazy
from .models import task, area
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages


from .forms import TaskCreateModelForm, TaskUpdateModelForm, TaskModelFormsetFactoryModelForm, TaskInlineFormsetFactoryModelForm, GardenTaskInlineFormsetFactoryModelForm
from .forms import AreaMultiEditForm, WorkSheetForm, AreaFocusForm
#
# LIST VIEW for task: display list of all tasks
# template: wi/task_list.html
#
class wi_listview(LoginRequiredMixin, ListView):
    model = task
 
#
# CREATE CRUD for task
# template: wi/task_create.html
#
class wi_create(LoginRequiredMixin, CreateView):
    #
    # models and forms
    #
    model = task
    form_class = TaskCreateModelForm

    template_name_suffix = '_create'
    #success_url = reverse_lazy('wi:wi_listview')
    
    def get_success_url(self):
        # set the success url view method where we have the object to access its id for the pk
        messages.add_message(self.request, messages.SUCCESS, f'New {self.object.area}  task added.')
        return reverse_lazy('wi:wi_listview')

#
# READ CRUD for task
# template: wi/task_detail.html - context contains object, not form
#
class wi_read(LoginRequiredMixin, DetailView):
    model = task
    fields = '__all__'

#
# UPDATE CRUD for task
# template: wi/task_form.html - context contains form
#
class wi_update(LoginRequiredMixin, UpdateView):
    model = task
    form_class = TaskUpdateModelForm

    def get_success_message(self, cleaned_data):
        return "Task {id} created successfully." % {'id': self.object.id}

    def get_success_url(self):
        # set the success url view method where we have the object to access its id for the pk
        message_task = self.get_object()
        messages.add_message(self.request, messages.SUCCESS, f'Task {message_task.id} successfully updated.')
        #return reverse_lazy('wi:wi_read', args=(message_task.id,))
        return reverse_lazy('wi:wi_listview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myid'] = self.object.id
        return context

#
# UPDATE DELETE for task
# template: wi/task_confirm_delete.html - context 
#
class wi_delete(LoginRequiredMixin, DeleteView):
    model = task
    fields = '__all__'
    # this is not a form based class, so do not use form classes
    #form_class = TaskDeleteModelForm

    success_url = reverse_lazy('wi:wi_listview')

    def get_success_message(self):
        delete_success_message = f"Task { self.object.id } deleted successfully."
        messages.add_message(self.request, messages.SUCCESS, delete_success_message)
        return delete_success_message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myid'] = self.object.id
        return context

#
# modelformset factory
#
@login_required
def task_modelformsetfactory(request):
    #
    # function based implementation of modelformsetfactory
    #
    task_modelformset = modelformset_factory(
                            task,
                            form=TaskModelFormsetFactoryModelForm, 
                            #fields=('priority', 'description', 'status', 'created', 'area'),
                            extra=4,
                            can_delete = True,
                        )

    if request.method == 'POST':
        formset = task_modelformset(request.POST, request.FILES)
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            formset.save()
            return redirect(reverse('wi:wi_listview'))
        else:
            #
            # TODO POST ERROR MESSAGE or just send back the data via post..?
            #
            messages.add_message(request, messages.INFO, f'formset not valid')
            return redirect(reverse('wi:wi_listview'))
    else:
        #
        # Otherwise, its a GET method call, instantiate TaskFormset (from database) and 
        # pass to template for render
        #
        formset = task_modelformset()

    return render(request, 'wi/task_modelformsetfactory.html', {'formset': formset})

#
# inline formset factory
#
@login_required
def task_inlineformsetfactory(request):
    task_inlineformset = inlineformset_factory(
                                                area,
                                                task,form=TaskInlineFormsetFactoryModelForm,
#                                                fields=('priority', 'status', 'description', 'created',),
                                                extra=2,
                                                can_delete=True,
                                            )
    if request.method == 'POST':
        formset = task_inlineformset(request.POST, request.FILES, instance=area.objects.get(name='Garden'))
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            formset.save()
            return redirect(reverse('wi:wi_listview'))
        else:
            #
            # form invalid could be many things...
            #
            messages.add_message(request, messages.ERROR, f'Changes not saved: data entry invalid')
            return redirect(reverse('home:darwin_root'))
    else:
        #
        # Otherwise, its a GET method call, create the TaskFormset and 
        # pass to dispaly template
        #
        inlinearea = area.objects.get(name='Garden')
        formset = task_inlineformset(instance=inlinearea)

    return render(request, 'wi/task_inlineformsetfactory.html', {'formset': formset})

@login_required
def card_investigation(request):
    garden_task = inlineformset_factory(
                                        area,
                                        task,
                                        form=GardenTaskInlineFormsetFactoryModelForm, 
                                        extra=2,
                                        can_delete = False,
                                        )

    home_task = inlineformset_factory(
                                    area,
                                    task,
                                    form=GardenTaskInlineFormsetFactoryModelForm, 
                                    extra=2,
                                    can_delete = False,
                                    )

    bike_task = inlineformset_factory(
                                    area,
                                    task,
                                    form=GardenTaskInlineFormsetFactoryModelForm, 
                                    extra=2,
                                    can_delete = False,
                                    )
    if request.method == 'POST':
        #
        # cooltip: test for which button was pressed uses the html button's name field. 
        #          Check if the html button name is in POST and you'll know if it was pressed.
        #
        if 'garden_update' in request.POST:
            formset = garden_task(request.POST, request.FILES, instance=area.objects.get(name='Garden'))
            area_modified = 'Garden'
        
        if 'home_update' in request.POST:
            formset = home_task(request.POST, request.FILES, instance=area.objects.get(name='Home'))
            area_modified = 'Home'
        
        if 'bike_update' in request.POST:
            formset = home_task(request.POST, request.FILES, instance=area.objects.get(name='Bike'))
            area_modified = 'Bike'

        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            formset.save()
            messages.add_message(request, messages.SUCCESS, f'{area_modified} tasks updated successfully')
            return redirect(reverse('wi:cards'))
        else:
            #
            # form invalid could be many things...
            #
            messages.add_message(request, messages.ERROR, f'{area_modified} changes not saved. {formset.non_form_errors()}')
            return redirect(reverse('home:darwin_root'))
    else:
        #
        # Otherwise, its a GET method call, create the TaskFormset and 
        # pass to dispaly template
        #
        garden_area = area.objects.get(name='Garden')
        home_area = area.objects.get(name='Home')
        bike_area = area.objects.get(name='Bike')
        garden_formset = garden_task(instance=garden_area)
        home_formset = home_task(instance=home_area)
        bike_formset = bike_task(instance=bike_area)

    return render(request, 'wi/card_investigation.html', {
                                                            'garden_formset': garden_formset,
                                                            'home_formset': home_formset,
                                                            'bike_formset': bike_formset }
                )

#
# MULTI-EDIT for Area
#
@login_required 
def area_multiedit(request):
    #
    # function based implementation of modelformsetfactory
    #
    area_multiedit_formset = modelformset_factory(
                                area,
                                form=AreaMultiEditForm, 
                                extra=4,
                                can_delete = True,
                            )

    if request.method == 'POST':
        formset = area_multiedit_formset(request.POST, request.FILES)
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            formset.save()
            return redirect(reverse('wi:area_multiedit'), {'formset': formset})
        else:
            #
            # TODO POST ERROR MESSAGE or just send back the data via post..?
            #
            messages.add_message(request, messages.INFO, f'formset not valid')
            return redirect(reverse('wi:area_multiedit'))
    else:
        #
        # Otherwise, its a GET method call, instantiate TaskFormset (from database) and 
        # pass to template for render
        #
        formset = area_multiedit_formset()

    return render(request, 'wi/area_multiedit.html', {'formset': formset})

#
# WORKSHEET for Task
#
@login_required
def task_worksheet(request):
    #
    # Create list of area names
    #
    area_list = list(area.objects.values_list('name', flat=True))
    #
    # formsetfactor for use throughout
    #
    formsetfactory = inlineformset_factory(
                                    area,
                                    task,
                                    form=WorkSheetForm, 
                                    extra=5,
                                    can_delete = False,
                                )

    #
    # First handle post case (where one of the forms requires updating)
    #
    if request.method == 'POST':
        clicked_area = ''
    
        for area_name in area_list:
            if area_name.lower() in request.POST:
                clicked_area = area_name
                break
            else:
                continue
         
        if clicked_area == '':

            #
            # somehow received post without a button click so will log an error
            #
            messages.add_message(request, messages.ERROR, f' No area button was clicked, no data saved.')
            return redirect(reverse('home:darwin_root'))            
        else:
            formset = formsetfactory(request.POST, request.FILES, instance=area.objects.get(name=clicked_area))

            if formset.is_valid():
                #
                # We have good data, save and return to listview
                #
                formset.save()
                messages.add_message(request, messages.SUCCESS, f'{clicked_area} tasks updated successfully')
                #Previously return to home_root,but would rather stay in worksheet. Hence just drop through to render below.
                #return redirect(reverse('wi:task_worksheet'))
            else:
                #
                # form invalid could be many things...
                #
                messages.add_message(request, messages.ERROR, f'{clicked_area} changes not saved. {formset.non_form_errors()}')
                #Previously return to home_root,but would rather stay in worksheet. Hence just drop through to render below.
                #return redirect(reverse('wi:task_worksheet'))

    #
    # Otherwise, its a GET method call, create the TaskFormset and 
    # pass to dispaly template
    #
    # iterate over all areas creating list of forms to use in the template
    #
    form_list = list()
    for area_name in area_list:
        form_list.append(formsetfactory(instance=area.objects.get(name=area_name)))
    # zip lists together so then can be mutually iterated in the template
    area_form_list = zip(area_list, form_list)

    return render(request, 'wi/task_worksheet.html', { 'area_form_list' : area_form_list })

#
# FOCUS VIEW for Tasks from a single Area
#
@login_required
def area_focus(request, area_name):
    area_formset_factory = inlineformset_factory(
                                                area,
                                                task,
                                                form=AreaFocusForm,
                                                extra=10,
                                                can_delete=True,
                                            )
    if request.method == 'POST':
        formset = area_formset_factory(
                                        request.POST, 
                                        request.FILES, 
                                        instance=area.objects.get(name=area_name)
                                    )
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            formset.save()
            messages.add_message(request, messages.SUCCESS, f'tasks updated successfully')
            return redirect(reverse_lazy('wi:task_areafocus', args=(area_name,)))
        else:
            #
            # form invalid could be many things...
            #
            messages.add_message(request, messages.ERROR, f'Changes not saved: data entry invalid {formset.errors}')
            return redirect(reverse_lazy('wi:task_areafocus', args=(area_name,)))
    else: # GET processing
        #
        # Create formset using specified object
        #
        area_object = area.objects.get(name=area_name)
        formset = area_formset_factory(instance=area_object)

    return render(
                    request, 
                    'wi/area_focus.html', {
                                            'area_name' : area_name,
                                            'formset': formset
                                        }
                )