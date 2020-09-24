from django.urls import path

from . import views
#from django.contrib.auth import views as auth_views

urlpatterns = [
    path('adgroups', views.build_adgroups, name='build_adgroups'),
    path('autobuilder', views.autobuilder, name='autobuilder'),
]