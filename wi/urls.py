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
        return mydate

    def to_url(self, value):

        return value

register_converter(DateConverter, 'yyyy-mm-dd')


rest_api_patterns = [
     #
     # Django REST Framework APIs
     #
     path('', views.api_root, name='api_root' ),
     path('domains/', views.domain_ListCreateAPIView.as_view(), name='rest_domains' ),
     path('domain/<int:pk>', views.domain_RetrieveUpdateDestroyAPIView.as_view(), name='rest_domain' ),
     path('areas/', views.area_ListCreateAPIView.as_view(), name='rest_areas' ),
     path('area/<int:pk>', views.area_RetrieveUpdateDestroyAPIView.as_view(), name='rest_area' ),
     path('tasks/', views.task_ListCreateAPIView.as_view(), name='rest_tasks' ),
     path('task/<int:pk>', views.task_RetrieveUpdateDestroyAPIView.as_view(), name='rest_task' ),

     #path('users/', views.user_ListCreateAPIView.as_view(), name='rest_users' ),
     #path('user/<int:pk>', views.user_RetrieveUpdateDestroyAPIView.as_view(), name='rest_user' ),
     #path('profiles/', views.profile_ListCreateAPIView.as_view(), name='rest_profiles' ),
     #path('profile/<int:pk>', views.profile_RetrieveUpdateDestroyAPIView.as_view(), name='rest_profile' ),
]


urlpatterns = [

    #
    # url patterns for task management
    #  
    path('task_worksheet/', views.task_worksheet, name='task_worksheet'),
    path('areafocus/<int:pk>', views.area_focus, name='task_areafocus'),
    path('area/', views.area_multiedit, name='area_multiedit'),
    path('domain/', views.domain_multiedit, name='domain_multiedit'),
    path('month_calendarview/', views.month_calendarview, name='month_calendarview'),
    path('day_calendarview/<yyyy-mm-dd:ymd_date>/', views.day_calendarview, name='day_calendarview'),
    #
    # AJAX URLs
    #
    path('task_delete/', views.task_delete, name='task_delete'),

    #
    # debug code
    #
    path('modal_test/', TemplateView.as_view(template_name='wi/modal_test.html'), name='modal_test'),
 
    #
    # link REST API patterns
    #
    path('api/', include(rest_api_patterns)),
 ]
