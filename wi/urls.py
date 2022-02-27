from django.urls import path

from . import views

#
# register namespace
#
app_name = 'wi'

urlpatterns = [
    #
    # url patterns for task management
    #
    path('task_worksheet', views.task_worksheet, name='task_worksheet'),
    path('areafocus/<int:pk>', views.area_focus, name='task_areafocus'),
    path('area', views.area_multiedit, name='area_multiedit'),
    path('domain', views.domain_multiedit, name='domain_multiedit'),
    path('month_calendarview', views.month_calendarview, name='month_calendarview'),
 ]
