from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import domain, area, task

from django.contrib import messages
from django.db.models import Max

from .forms import DomainMultiEditForm, AreaMultiEditForm, WorkSheetForm, AreaFocusForm


#
# Tasks Display
#
@login_required
def task_worksheet(request):

    #
    # session handling: check and set initial conditions: 0th domain displayed,
    # do not show_done and seven day session expiry
    #
    if not 'display_domain' in request.session:
        request.session['display_domain'] = 0
        request.session.set_expiry(7 * 24 * 60 * 60)

    if not 'show_done' in request.session:
        request.session['show_done'] = False



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

    index = request.session['display_domain']
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
    
    # set render domain after processing domain navigation buttons
    render_domain = domains[index]

    #
    # process hide/show button
    #
    if 'show_done' in request.POST:
        request.session['show_done'] = True
    elif 'hide_done' in request.POST:
        request.session['show_done'] = False

    #
    # process user order buttons (django-order-model library)
    # N.B. library is 'area.hide' unaware, so had to add code to skip hidden areas
    #
    if 'navigate_up' in request.POST:
        a = area.objects.get(name=request.POST['navigate_up'])

        # up button = .previous()
        # if a.previous = None, exit
        # if a.previous.hide = False, a.up and exit
        # if a.previous.hide = True, a.up and continue
        while a.previous() != None:
            if a.previous().hide == True:
                a.up()
            else:
                a.up()
                break

    elif 'navigate_down' in request.POST:
        a = area.objects.get(name=request.POST['navigate_down'])
        # 
        # down button = .next()
        # if a.next = None, exit
        # if a.next.hide = False, a.down and exit
        # if a next.hide = True, a.down and contine
        while a.next() != None:
            if a.next().hide == True:
                a.down()
                print('down and skipping hidden')
            else:
                a.down()
                print('down, done due to not hidden')
                break

    #
    # Create list of area names. The case of user with no areas handled in template
    #
    area_list = list(area.objects.filter(created_by=request.user
                                ).filter(domain=current_domain
                                ).exclude(hide=True))

    #
    # formsetfactory for use throughout this view
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
        success_areas = list()

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
                        # TODO: this works but should provably be checked for haschanged/valid and retested
                        if not form.instance.created_by:
                            form.instance.created_by = request.user

                        #
                        # set/clear completed date for changed fields
                        #
                        if form.has_changed() and form.is_valid():
                            if 'status' in form.changed_data:
                                if form.cleaned_data['status']:
                                    form.instance.completed = timezone.now()
                                else:
                                    form.instance.completed = None

                    formset.save()
                    # processing multiple formset so flash message handling is aggregated
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
                            ).filter(domain=render_domain
                            ).exclude(hide=True))

    form_list = list()
    retention_date = timezone.now() - timezone.timedelta(days = render_domain.retain_completed_tasks)

    #
    # prep queryset for use in factory honoring the hide/show done settings
    #
    qs = task.objects.filter(created_by = request.user)

    if not request.session['show_done']:
        qs = qs.filter(Q(completed__gt = retention_date) | Q(completed = None))

    qs = qs.order_by('status', '-priority')

    for area_obj in area_list:
        form_list.append(formsetfactory(queryset=qs,
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
                                                        'domain_count' : domains_length,
                                                        'show_done' : request.session['show_done'], })

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
                                                                ).exclude(hide=True)

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

                if form.has_changed() and form.is_valid():
                    #
                    # set/clear completed date for changed fields
                    #
                    if 'status' in form.changed_data:
                        if form.cleaned_data['status']:
                            form.instance.completed = timezone.now()
                        else:
                            form.instance.completed = None



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
        retention_date = timezone.now() - timezone.timedelta(days = area_obj.domain.retain_completed_tasks)
        print(f'area_focus retention date = {retention_date}')

        formset = area_formset_factory(queryset=task.objects.filter(created_by=request.user
                                                            ).filter(area=area_obj.id
                                                            ).filter(Q(completed__gt = retention_date) | Q(completed = None)
                                                            ).order_by('status', '-priority'))


        return render(request, 'wi/area_focus.html', {'area_name' : area_obj.name,
                                                        'formset': formset } )

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
        formset = domain_factory(queryset=domain.objects.filter(created_by=request.user
                                                        ).order_by('name'))

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

                #
                # the django-ordered-model library fails to handle case when domain changes. They
                # actually have a bug open for it, not fixed. So the hack is to find the max
                # order value in the new domain and change the order value on the area to max + 1
                # which sets an area added to a new domain at bottom of the list.
                #
                if 'domain' in form.changed_data:
                    new_domain = form.cleaned_data['domain']
                    new_max = area.objects.filter(created_by = request.user
                                        ).filter(domain__name = new_domain
                                        ).aggregate(Max('order'))
                    # max returns None if there are no areas in the new domain
                    if new_max['order__max'] == None:
                        form.instance.order = 0
                    else:
                        form.instance.order = new_max['order__max'] + 1
                    # in case more than one area moved to a new domain, save this form now
                    form.save()
                    print(f'{new_domain} {new_max["order__max"]} {form.instance.order}')

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
        formset = area_factory(queryset=area.objects.filter(created_by=request.user
                                                    ).order_by('domain__name', 'hide', 'name'))


    return render(request, 'wi/area_multiedit.html', {'formset': formset})