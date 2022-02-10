from django.views.generic import ListView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse, reverse_lazy
from .models import domain, area, task
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages


from .forms import TaskCreateModelForm, TaskUpdateModelForm, TaskModelFormsetFactoryModelForm, TaskInlineFormsetFactoryModelForm, GardenTaskInlineFormsetFactoryModelForm
from .forms import DomainMultiEditForm, AreaMultiEditForm, WorkSheetForm, AreaFocusForm
#
# LIST VIEW for task: display list of all tasks
# template: wi/task_list.html
#
class wi_listview(LoginRequiredMixin, ListView):
    model = task

    #
    # hook get_queryset to limit access to tasks created by the logged in user
    #
    def get_queryset(self):
        q = super(wi_listview, self).get_queryset()
        return q.filter(created_by=self.request.user)
 
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
    # use form_valid to catch and set created_by to the logged in user. Works becuase it's
    # CreateView class based. Link below. This is readily extended to non-class views.
    # https://docs.djangoproject.com/en/4.0/topics/class-based-views/generic-editing/#models-and-request-user
    #
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

#
# READ CRUD for task
# template: wi/task_detail.html - context contains object, not form
#
class wi_read(LoginRequiredMixin, DetailView):
    model = task
    fields = '__all__'

    #
    # hook get_queryset to limit access to tasks created by the logged in user
    # TODO: as this is a single read view, user will get error 404 if they try to read another user's
    # data perhaps we could do something smarter...
    def get_queryset(self):
        q = super(wi_read, self).get_queryset()
        return q.filter(created_by=self.request.user)

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
                            extra=4,
                            can_delete = True,
                        )

    if request.method == 'POST':
        formset = task_modelformset(request.POST, request.FILES)
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            # but first scan the formsets and instatiate the user that created the task
            # originally tried to used the form or the cleaned data, and of course the
            # model doesn't incldue createdby. however the form does refer to the instance
            # and so that can be modified.
            #
            for form in formset:
                if not form.instance.created_by:
                    form.instance.created_by = request.user

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
        formset = task_modelformset(queryset=task.objects.filter(created_by=request.user))

    return render(request, 'wi/task_modelformsetfactory.html', {'formset': formset})

#
# inline formset factory
#
@login_required
def task_inlineformsetfactory(request):
    task_inlineformset = inlineformset_factory(
                                                area,
                                                task,form=TaskInlineFormsetFactoryModelForm,
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
#
# MULTI-EDIT for Domain
#
@login_required 
def domain_multiedit(request):
    #
    # function based implementation of modelformsetfactory
    #
    domain_factory = modelformset_factory(
                                domain,
                                form=DomainMultiEditForm, 
                                extra=4,
                                can_delete = True,
                            )

    if request.method == 'POST':
        formset = domain_factory(request.POST, request.FILES)
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            # but first scan the formsets and instatiate the user that created the task
            # originally tried to used the form or the cleaned data, and of course the
            # model doesn't incldue createdby. however the form does refer to the instance
            # and so that can be modified.
            #
            for form in formset:
                if not form.instance.created_by:
                    form.instance.created_by = request.user

            formset.save()
            messages.add_message(request, messages.SUCCESS, f'Domains updated successfully')
            return redirect(reverse('wi:domain_multiedit'), {'formset': formset})
        else:
            #
            # TODO POST ERROR MESSAGE or just send back the data via post..?
            #
            messages.add_message(request, messages.INFO, f'Domain formset not valid')
            return redirect(reverse('wi:area_multiedit'))
    else:
        #
        # Otherwise, its a GET method call, instantiate TaskFormset (from database) and 
        # pass to template for render
        #
        formset = domain_factory(queryset=domain.objects.filter(created_by=request.user))

    return render(request, 'wi/domain_multiedit.html', {'formset': formset})
#
# MULTI-EDIT for Area
#
@login_required 
def area_multiedit(request):
    #
    # function based implementation of modelformsetfactory
    #
    AreaMultiEditForm.base_fields['domain'].queryset = domain.objects.filter(created_by = request.user)

    area_factory = modelformset_factory(
                                area,
                                form=AreaMultiEditForm, 
                                extra=4,
                                can_delete = True,
                            )

    if request.method == 'POST':
        formset = area_factory(request.POST, request.FILES)
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            # but first scan the formsets and instatiate the user that created the task
            # originally tried to used the form or the cleaned data, and of course the
            # model doesn't incldue createdby. however the form does refer to the instance
            # and so that can be modified.
            #
            for form in formset:
                if not form.instance.created_by:
                    form.instance.created_by = request.user

            formset.save()
            messages.add_message(request, messages.SUCCESS, f'Areas updated successfully')
            return redirect(reverse('wi:area_multiedit'), {'formset': formset})
        else:
            #
            # TODO POST ERROR MESSAGE or just send back the data via post..?
            #
            messages.add_message(request, messages.INFO, f'formset not valid: {formset.errors}')
            return redirect(reverse('wi:area_multiedit'))
    else:
        #
        # Otherwise, its a GET method call, instantiate TaskFormset (from database) and 
        # pass to template for render
        #
        formset = area_factory(queryset=area.objects.filter(created_by=request.user))


    return render(request, 'wi/area_multiedit.html', {'formset': formset})
#
# WORKSHEET for Task
#
@login_required
def task_worksheet(request):

    #
    # session handling: check and set initial condition, 0th domain and one day session expiry
    #
    if not 'display_domain' in request.session:
        request.session['display_domain'] = 0
        request.session.set_expiry(24 * 60 * 60)

    index = request.session['display_domain']

    #
    # process domain navigation buttons.
    # todo: couldn't determine a more pythonic means to iterate forward/backward
    #       across the domains, hence implementation is C-like.
    #
    domains = domain.objects.filter(created_by=request.user)
    #
    # if the user somehow has no domains, render template setting domain_count to zero
    # and the template will handle.
    #
    if not domains:
        return render(request, 'wi/task_worksheet.html', {'domain_count' : 0, })

    current_domain = domains[index]

    domains_length = len(domains)

    if domains_length > 1:

        if 'domain_right' in request.POST:
            index = index + 1
            if index == domains_length:
                index = 0
            request.session['display_domain'] = index

        elif 'domain_left' in request.POST:
            if index == 0:
                index = domains_length - 1
            else:
                index = index - 1
            request.session['display_domain'] = index

    else:
        #
        # if there is only one domain, there is no possible work to be done.
        #
        pass
    
    # set render domain after processing domain navigation buttons
    render_domain = domains[index]

    #
    # Create list of area names. The case of user with no areas handled in template
    # .values_list(): https://docs.djangoproject.com/en/stable/ref/models/querysets/#values-list
    #
    area_list = list(area.objects.filter(created_by=request.user
                                ).filter(domain=current_domain))
#                                ).values_list('name', flat=True))
    success_areas = list()

    #
    # formsetfactory for use throughout
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
        #
        # iterate through all formset, one for each area
        #
        for area_obj in area_list:
            #
            # create formset for each area. Prefix required when using more than one formset per page.
            #
            formset = formsetfactory(request.POST,
                                    request.FILES,
                                    prefix = area_obj.name,
                                    instance=area.objects.get(pk=area_obj.id),
                                    )
            #
            # parse/handle only those formset that changed
            #
            if formset.has_changed(): 
                #
                # handle data valid vs invalid
                #
                if formset.is_valid():
                    #
                    # We have good data, save and return to listview
                    #
                    # but first scan the formsets and instatiate the user that created the task
                    # originally tried to used the form or the cleaned data, and of course the
                    # model doesn't incldue createdby. however the form does refer to the instance
                    # and so that can be modified.
                    #
                    for form in formset:
                        if not form.instance.created_by:
                            form.instance.created_by = request.user

                    formset.save()
                    # potentially processing multiple formset so flash message handling is aggregated
                    success_areas.append(area_obj.name)

                else:
                    #
                    # form invalid could be many things...
                    #
                    messages.add_message(request, messages.ERROR, f'{area_obj.name} changes not saved. {formset.non_form_errors()}')

            else:
                #
                # else pass for formset where data didn't change, can delete this later
                #
                pass

        if success_areas:
            areas_string = ', '.join(str(a) for a in success_areas)
            messages.add_message(request, messages.SUCCESS, f'{areas_string} tasks updated successfully')

    #
    # Otherwise, its a GET method call, create the TaskFormset and 
    # pass to dispaly template. Also the POST method falls through to here.
    #
    # iterate over all areas creating list of forms to use in the template
    #
    area_list = list(area.objects.filter(created_by=request.user
                            ).filter(domain=render_domain))

    form_list = list()
    for area_obj in area_list:
        form_list.append(formsetfactory(queryset=task.objects.filter(created_by=request.user),
                                        prefix = area_obj.name,
                                        instance=area.objects.get(pk=area_obj.id)))
    #
    # zip lists together so then can be mutually iterated in the template
    #
    area_form_list = zip(area_list, form_list)
    # convert zip object to list so django template can use |length filter (hack)
    afl = list(area_form_list)

    return render(request, 'wi/task_worksheet.html', { 'area_form_list' : afl,
                                                        'domain_name' : render_domain.name,
                                                        'domain_count' : domains_length, })

#
# FOCUS VIEW for Tasks from a single Area
#
@login_required
def area_focus(request, pk):

    area_obj = area.objects.get(pk=pk)

    #
    # Area focus must not disply choice options that belong to other users. Forms enable
    # us to override the queryset selecting the values to be displayed.
    #
    AreaFocusForm.base_fields['area'].queryset = area.objects.filter(created_by = request.user
                                                                ).filter(domain=area_obj.domain)

    area_formset_factory = modelformset_factory(task,
                                                form=AreaFocusForm,
                                                extra=5,
                                                can_delete=True,
                                            )
    if request.method == 'POST':
        formset = area_formset_factory(
                                        request.POST, 
                                        request.FILES, 
                                        queryset=task.objects.filter(created_by=request.user).filter(area=area_obj)
                                    )
        if formset.is_valid():
            #
            # We have good data, save and return to listview
            #
            for form in formset:
                if not form.instance.created_by:
                    form.instance.created_by = request.user
            
            formset.save()
            messages.add_message(request, messages.SUCCESS, f'{area_obj.name} tasks updated successfully')
            return redirect(reverse_lazy('wi:task_areafocus', args=(pk,)))
        else:
            #
            # form invalid could be many things...
            #
            messages.add_message(request, messages.ERROR, f'Changes not saved: data entry invalid {formset.errors}')
            return redirect(reverse_lazy('wi:task_areafocus', args=(pk,)))
    else: # GET processing
        #
        # Create formset using specified object
        #
        formset = area_formset_factory(queryset=task.objects.filter(created_by=request.user).filter(area=area_obj.id))

    return render(request, 'wi/area_focus.html', {'area_name' : area_obj.name,
                                                    'formset': formset } )
