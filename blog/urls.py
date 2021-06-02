from django.urls import path
from django.conf.urls import url
from . import views
from django.conf import settings
from blog import views

urlpatterns = [
    url(r'^accounts/login/$', views.login, name='login'),
]

urlpatterns = [
    path('', views.IndexPage.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('registr', views.regist, name='regist'),
    path('index_day/', views.index_day, name='index_day'),
    path('index_night/', views.index_night, name='index_night'),
]