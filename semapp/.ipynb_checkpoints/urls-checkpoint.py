from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.build_adgroups, name='build_adgroups'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='semapp/login.html')),
#    path('show', views.type_first_file, name='show'),
]