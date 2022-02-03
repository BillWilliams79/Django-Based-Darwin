from django.urls import path

from . import views

#
# register namespace
#
app_name = 'wi'

urlpatterns = [
    #
    # List View - CRUD paths
    #
    path('', views.wi_listview.as_view(), name='wi_listview'), #template = task_list.html
    path('create/', views.wi_create.as_view(), name='wi_create'), #template = task_create.html
    path('<int:pk>', views.wi_read.as_view(), name='wi_read'), # template = task_detail.html
    path('<int:pk>/update', views.wi_update.as_view(), name = 'wi_update'), # template = task_form.html
    path('<int:pk>/delete', views.wi_delete.as_view(), name = 'wi_delete'), # template = task_confirm_delete.html
    path('modelformfactory', views.task_modelformsetfactory, name='task_modelformsetfactory'), # template = task_modelformsetfactory.html
#    path('inlineformfactory', views.task_inlineformsetfactory, name='task_inlineformsetfactory'), # template = task_inlineformsetfactory.html
    path('area', views.area_multiedit, name='area_multiedit'),
    path('task_worksheet', views.task_worksheet, name='task_worksheet'), # template = task_worksheet.html
    path('areafocus/<slug:area_name>', views.area_focus, name='task_areafocus'), # template = task_areafocus.html
#    path('task_playground', views.task_playground.as_view(), name='task_playground'), # template = task_playground.html

  #
  # / - <object>_roda: read only display all 
  # /create - <object>_create
  # /<int:pk>/update - <object>_update
  # /<int:pk>/delete - <object>_delete
  # /worksheet - <object>_worksheet: custom per area view
  # /areafocus/<slug:slug> - inlineformset view of tasks by <slug> area. URL design doubts weigh heavily.
  #
 ]
