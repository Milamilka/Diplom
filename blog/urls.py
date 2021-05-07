from django.urls import path
from django.conf.urls import url
from . import views
from django.conf import settings

urlpatterns = [
    url(r'^accounts/login/$', views.login, name='login'),
]

urlpatterns = [
    path('', views.IndexPage.as_view(), name='index'),
]