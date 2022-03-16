from django.urls import include, path, register_converter
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns

from datetime import datetime

from . import views

#
# register namespace
#
app_name = 'wi'

#
# data convertor to match dates in this format:
# yyyy-mm-dd or '%Y-%m-%d'
# created initially for day_calendarview
#
class DateConverter:

    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    def to_python(self, value):
        mydate = datetime.strptime(value, '%Y-%m-%d')
        print(f'dataconverter.to_python: {mydate}')
        return mydate

    def to_url(self, value):
        return value

register_converter(DateConverter, 'yyyy-mm-dd')


rest_api_patterns = [
     #
     # Django Rest Framework APIs
     # - task
     # - not valid REST architecturally.
     #
     path('', views.api_root, name='api_root' ),
     #path('task_list', views.task_list, name='task_list' ),
     #path('task_view/<int:pk>', views.task_view, name='task_view' ),
     #path('task_update/<int:pk>', views.task_update, name='task_update' ),
     #path('task_create', views.task_create, name='task_create' ),
     #path('task_delete/<int:pk>', views.task_delete, name='task_delete' ),
     #
     # = area
     #
     #path('area_view/<int:pk>', views.area_view, name='area_view' ),

     # class based views
     #
     # Area: generic views, generic model
     #
     #path('area_ListAPIView', views.area_ListAPIView.as_view(), name='area_ListAPIView' ),

     #
     # attempt #1 at tasks restful api without User support, just class based domain, area, task
     # and it filters based on the user.
     #
     #path('area_RetrieveAPIView/<int:pk>', views.area_RetrieveAPIView.as_view(), name='area_RetrieveAPIView' ),
     #path('area_ListCreateAPIView', views.area_ListCreateAPIView.as_view(), name='area_ListCreateAPIView' ),
     path('domains/', views.domain_ListCreateAPIView.as_view(), name='rest_domains' ),
     path('domain/<int:pk>', views.domain_RetrieveUpdateDestroyAPIView.as_view(), name='rest_domain' ),
     path('areas/', views.area_ListCreateAPIView.as_view(), name='rest_areas' ),
     path('area/<int:pk>', views.area_RetrieveUpdateDestroyAPIView.as_view(), name='rest_area' ),
     path('tasks/', views.task_ListCreateAPIView.as_view(), name='rest_tasks' ),
     path('task/<int:pk>', views.task_RetrieveUpdateDestroyAPIView.as_view(), name='rest_task' ),
     
]

urlpatterns = [

    #
    # url patterns for task management
    #  
    path('task_worksheet/',
         views.task_worksheet,
         name='task_worksheet'),
    
    path('areafocus/<int:pk>',
         views.area_focus,
         name='task_areafocus'),
    
    path('area/',
         views.area_multiedit,
         name='area_multiedit'),
    
    path('domain/',
         views.domain_multiedit,
         name='domain_multiedit'),
    
    path('month_calendarview/',
         views.month_calendarview,
         name='month_calendarview'),
    
    path('day_calendarview/<yyyy-mm-dd:ymd_date>/',
         views.day_calendarview,
         name='day_calendarview'),
    
    path('modal_test/',
         TemplateView.as_view(template_name='wi/modal_test.html'),
         name='modal_test'),
    
    path('task_delete/',
         views.task_delete,
         name='task_delete'),
 
    #
    # link the rest patterns
    #
    path('api/', include(rest_api_patterns)),
 ]
