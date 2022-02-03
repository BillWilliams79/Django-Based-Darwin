from django.urls import path
from django.views.generic import TemplateView

#
# register namespace
#
app_name = 'home'

urlpatterns = [
    #
    # home page
    #
    path('', TemplateView.as_view(template_name='home/index.html'), name="darwin_root"),
 ]
