from django.urls import path
from . import views

urlpatterns = [path('', views.exp, name='exp'),]
