from django.urls import path, register_converter
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

urlpatterns = [
    #
    # url patterns for task management
    #
    path('task_worksheet', views.task_worksheet, name='task_worksheet'),
    path('areafocus/<int:pk>', views.area_focus, name='task_areafocus'),
    path('area', views.area_multiedit, name='area_multiedit'),
    path('domain', views.domain_multiedit, name='domain_multiedit'),
    path('month_calendarview', views.month_calendarview, name='month_calendarview'),
    path('day_calendarview/<yyyy-mm-dd:ymd_date>/', views.day_calendarview, name='day_calendarview'),
 ]
