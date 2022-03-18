from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import domain, area, task
from django.http import JsonResponse
import datetime as dt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse as rest_reverse
from rest_framework import generics
from wi.serializers import area_class_serializer, domain_class_serializer, task_class_serializer, user_class_serializer, profile_class_serializer
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework import permissions

from django.contrib import messages
from django.db.models import Max
from django.contrib.auth.models import User

from .forms import DomainMultiEditForm, AreaMultiEditForm, WorkSheetForm, AreaFocusForm
from users.models import Profile


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

    if not 'show_priority' in request.session:
        request.session['show_priority'] = False

    #
    # process domain navigation buttons.
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

    #
    # process domain naviagation buttons
    #
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
    # process hide/show button
    #
    if 'show_priority' in request.POST:
        request.session['show_priority'] = True
    elif 'hide_priority' in request.POST:
        request.session['show_priority'] = False

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
                                    extra=2,
                                    can_delete = False,
                                )

    #
    # POST processing
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
            # process only formsets that changed
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
                # formset didn't change, pass
                #
                pass

        if success_areas:
            areas_string = ', '.join(str(a) for a in success_areas)
            messages.add_message(request, messages.SUCCESS, f'{areas_string} tasks updated successfully')

        #
        # redirect/GET back to worksheet
        #
        return redirect(reverse_lazy('wi:task_worksheet'))

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

    # no filter required to show all
    if not request.session['show_done']:
        qs = qs.filter(Q(completed__gt = retention_date) | Q(completed = None))

    # no filter required to show all
    if not request.session['show_priority']:
        qs = qs.filter(priority = True)


    qs = qs.order_by('status', '-priority', '-updated')

    for area_obj in area_list:
        form_list.append(formsetfactory(queryset=qs,
                                        prefix = area_obj.name,
                                        instance=area.objects.get(pk=area_obj.id),))
    #
    # zip lists together so then can be mutually iterated in the template
    #
    area_form_list = zip(area_list, form_list)
    # convert zip object to list so django template can use |length filter
    afl = list(area_form_list)

    return render(request, 'wi/task_worksheet.html', { 'area_form_list' : afl,
                                                        'domain_name' : render_domain.name,
                                                        'domain_count' : domains_length,
                                                        'show_done' : request.session['show_done'],
                                                        'show_priority' : request.session['show_priority'], })

#
# Area View
#
@login_required
def area_focus(request, pk):

    #
    # instantiate session defaults if none 
    #
    if not 'show_done' in request.session:
        request.session['show_done'] = False

    #
    # process hide/show button
    #
    if 'show_done' in request.POST:
        request.session['show_done'] = True
    elif 'hide_done' in request.POST:
        request.session['show_done'] = False

    area_obj = area.objects.get(pk=pk)

    #
    # Area focus must not disply choice options that belong to other users. Forms enable
    # us to override the queryset selecting the values to be displayed.
    #
    #AreaFocusForm.base_fields['area'].queryset = area.objects.filter(created_by = request.user
    #                                                            ).exclude(hide=True)

    area_formset_factory = modelformset_factory(task,
                                                form=AreaFocusForm,
                                                extra=2,
                                                can_delete=True,
                                            )

    #
    # POST processing
    #
    if request.method == 'POST':

        formset = area_formset_factory(request.POST,
                                        request.FILES,
                                        queryset=task.objects.filter(created_by=request.user
                                                            ).filter(area=area_obj))

        if formset.has_changed():
            if formset.is_valid():
                #
                # We have good data, save and return to listview
                #
                print('formset has changed and is valid')
                for form in formset:
                    if not form.instance.created_by:
                        form.instance.created_by = request.user

                    if form.has_changed() and form.is_valid():
                        print(f'areafocus: {form.changed_data}')
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

            else:
                #
                # form is invalid, flash message with formset.errors
                #
                messages.add_message(request, messages.ERROR, f'Changes not saved: data entry invalid {formset.errors}')

        else:
            # POST called with no changes
            pass

        #
        #   redirect/GET after all post processing
        #
        return redirect(reverse_lazy('wi:task_areafocus', args=(pk,)))

    else:
        #
        # GET processing
        #
        retention_date = timezone.now() - timezone.timedelta(days = area_obj.domain.retain_completed_tasks)

        qs = task.objects.filter(created_by=request.user
                        ).filter(area=area_obj.id)

        # no filter required to show all
        if not request.session['show_done']:
            qs = qs.filter(Q(completed__gt = retention_date) | Q(completed = None))

        qs = qs.order_by('status', '-priority', '-updated')

        formset = area_formset_factory(queryset=qs)

        return render(request, 'wi/area_focus.html', {'area_name' : area_obj.name,
                                                        'formset': formset,
                                                        'show_done' : request.session['show_done'],
                                                         } )

#
# Domain Editor
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

        formset = domain_factory(request.POST,
                                request.FILES)

        if formset.has_changed():
            if formset.is_valid():
                #
                # We have good data, process created_by and save.
                #
                for form in formset:
                    if not form.instance.created_by:
                        form.instance.created_by = request.user

                formset.save()
                messages.add_message(request, messages.SUCCESS, f'Domains updated successfully')
            else:
                #
                # form is invalid, flash message with formset.errors
                #
                messages.add_message(request, messages.ERROR, f'Changes not saved: data entry invalid {formset.errors}')
        else:
            # no changes to formset
            pass

        #
        # redirect/GET back to area multi-edit
        #
        return redirect(reverse('wi:domain_multiedit'))
    else:
        #
        # GET processing, re-render page
        #
        formset = domain_factory(queryset=domain.objects.filter(created_by=request.user
                                                        ).order_by('name'))

    return render(request, 'wi/domain_multiedit.html', {'formset': formset})

#
# Area Editor
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

        formset = area_factory(request.POST,
                            request.FILES)
        if formset.has_changed():

            if formset.is_valid():
                #
                # formset changed and is valid, process created_by, order data
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
            else:
                #
                # form is invalid, flash message with formset.errors
                #
                messages.add_message(request, messages.ERROR, f'Changes not saved: data entry invalid {formset.errors}')
        else:
            # formset didn't change
            pass
        #
        # redirect/GET back to same page
        #
        return redirect(reverse('wi:area_multiedit'))

    else:
        #
        # GET processing, re-render page
        #
        formset = area_factory(queryset=area.objects.filter(created_by=request.user
                                                    ).order_by('domain__name', 'hide', 'name'))

    return render(request, 'wi/area_multiedit.html', {'formset': formset})

#
# Calendar MONTH view of completed tasks
#
@login_required
def month_calendarview(request):

    #
    # POST processing isnt' expected so we can post a warning.
    #
    if request.method == 'POST':
        messages.add_message(request, messages.WARNING, f'Month calendar view called in error as POST')
        return redirect(reverse_lazy('wi:month_calendarview'))

    #
    # calculate the days and start day for the calendar render
    #
    display_weeks = 4

    #
    #   given the display weeks, calculate a sunday for a number of weeks ago.
    #   input is number of weeks you want displayed. currently hard coded here.
    #   NB: using timezone.localtime as the time is used to determine the user's calendar view.
    #
    #daysthisweektoSunday = 0 if dt.datetime.isoweekday(today) == 7 else dt.datetime.isoweekday(today)
    #start_sunday_offset = (display_weeks - 1) * 7 + daysthisweektoSunday

    today = timezone.localtime(timezone.now())
    start_sunday_offset = (display_weeks - 1) * 7 + (dt.datetime.isoweekday(today) % 7)
    start_day = today - timezone.timedelta(days = start_sunday_offset)
    display_days = display_weeks * 7

    all_description_list = list()
    days_list = list()

    for loop_day in range(display_days):
        day_description_list = list()
        current_day = start_day + timezone.timedelta(loop_day)
        days_list.append(current_day)

        # iterate over the day's qs and create a list of descriptions
        qs = task.objects.filter(created_by = request.user
                        ).filter(status = True
                        ).filter(completed__date = current_day
                        ).filter(area__hide = False
                        ).order_by('status', '-priority')
        for t in qs:
            day_description_list.append(t.description)

        all_description_list.append(day_description_list)
    #
    # zip lists together so then can be mutually iterated in the template
    #
    month_data_list = zip(days_list, all_description_list)
    # convert zip object to list so django template can use |length filter
    mdl = list(month_data_list)

    return render(request, 'wi/month_calendarview.html', { 'month_data_list' : mdl,})

#
# Calendar DAY view of completed tasks
#
@login_required
def day_calendarview(request, ymd_date):

    #
    # POST processing isnt' expected so we can post a warning.
    #
    if request.method == 'POST':
        messages.add_message(request, messages.WARNING, f'Month calendar view called in error as POST')
        return redirect(reverse_lazy('wi:month_calendarview'))


    # correct example usage of .strptime to create a datetime object
    # dt1 = dt.datetime.strptime('2022-03-02', '%Y-%m-%d')
    # print(dt1)
    # mydate = '2022-03-31'
    # dt2 = dt.datetime.strptime(mydate, '%Y-%m-%d')
    # print(f'mydate conversion: {dt2}')

    #
    # Create calendar view with the provided date and render one day.
    # Voila, day view.
    #
    
 #   start_day = dt.datetime.strptime(slug, '%Y-%m-%d')
    #todo how does this fail?
    start_day = ymd_date
    print(start_day)
    display_days = 1
    all_description_list = list()
    days_list = list()

    for loop_day in range(display_days):
        day_description_list = list()
        current_day = start_day + timezone.timedelta(loop_day)
        days_list.append(current_day)

        # iterate over the day's qs and create a list of descriptions
        qs = task.objects.filter(created_by = request.user
                        ).filter(status = True
                        ).filter(completed__date = current_day
                        ).filter(area__hide = False
                        ).order_by('status', '-priority')
        for t in qs:
            day_description_list.append(t.description)

        all_description_list.append(day_description_list)
    #
    # zip lists together so then can be mutually iterated in the template
    #
    month_data_list = zip(days_list, all_description_list)
    # convert zip object to list so django template can use |length filter
    mdl = list(month_data_list)

    return render(request, 'wi/day_calendarview.html', { 'month_data_list' : mdl,})

#
# Area Editor
#
@login_required
def task_delete(request):
    
    print(request.POST)
    print(request.POST['id'])

    if request.method == 'POST':
        
        t = task.objects.get(pk = request.POST['id'])
        print(t.description)
        t.delete()
        return JsonResponse(data = {}, status=200)
    
    else:
        return JsonResponse(status=400)

##############################################################################
#
# RESTful API
# functional definitions (non-class)
#
# API ROOT
#
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    print(f'api root: {request.user}')
    return Response({
        'Application' : 'Darwin',
        'Domains' : rest_reverse('wi:rest_domains', request=request, format=format),
        'Areas' : rest_reverse('wi:rest_areas', request=request, format=format),
        'Tasks' : rest_reverse('wi:rest_tasks', request=request, format=format),
        #'User' : rest_reverse('wi:rest_users', request=request, format=format),
        #'Profile' : rest_reverse('wi:rest_profiles', request=request, format=format),
    })
    

#
# domain: List or Create one or more domains
#
class domain_ListCreateAPIView(generics.ListCreateAPIView):

    def get_queryset(self):
        user = self.request.user
        return domain.objects.filter(created_by = user)
    serializer_class = domain_class_serializer
    permission_classes = [permissions.IsAuthenticated]

#
# Read, Update, Delete a single domain (no create, no lists)
#
class domain_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):

    def get_queryset(self):
        user = self.request.user
        return domain.objects.filter(created_by = user)

    serializer_class = domain_class_serializer
    permission_classes = [permissions.IsAuthenticated]


#
# area: List or Create one or more areas
#
class area_ListCreateAPIView(generics.ListCreateAPIView):

    def get_queryset(self):
        user = self.request.user
        return area.objects.filter(created_by = user)

    #example of how to hook perform_create
    #def perform_create(self, serializer):
        # serializer.save(owner=self.request.user)

    serializer_class = area_class_serializer
    permission_classes = [permissions.IsAuthenticated]

#
# Read, Update, Delete a single area (no create, no lists)
#
class area_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):

    def get_queryset(self):
        user = self.request.user
        return area.objects.filter(created_by = user)

    serializer_class = area_class_serializer
    permission_classes = [permissions.IsAuthenticated]


#
# task: List or Create one or more tasks
#
class task_ListCreateAPIView(generics.ListCreateAPIView):

    def get_queryset(self):
        user = self.request.user
        return task.objects.filter(created_by = user)
    serializer_class = task_class_serializer
    permission_classes = [permissions.IsAuthenticated]

#
# Read, Update, Delete a single task (no create, no lists)
#
class task_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    
    def get_queryset(self):
        user = self.request.user
        return task.objects.filter(created_by = user)

    serializer_class = task_class_serializer
    permission_classes = [permissions.IsAuthenticated]


#
# User: List or Create one or more
#
class user_ListCreateAPIView(generics.ListCreateAPIView):

    def get_queryset(self):
        return User.objects.all()

    serializer_class = user_class_serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#
# Read, Update, Delete a single User (no create, no lists)
#
class user_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    
    def get_queryset(self):
        return User.objects.all()

    serializer_class = user_class_serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#
# profile: List or Create one or more 
#
class profile_ListCreateAPIView(generics.ListCreateAPIView):

    def get_queryset(self):
        return Profile.objects.all()

    serializer_class = profile_class_serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#
# Read, Update, Delete a single profile (no create, no lists)
#
class profile_RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    
    def get_queryset(self):
        return Profile.objects.all()

    serializer_class = profile_class_serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]






