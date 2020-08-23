from django.urls import path

from . import views

urlpatterns = [
    path('', views.build_adgroups, name='build_adgroups'),
#    path('show', views.type_first_file, name='show'),
]