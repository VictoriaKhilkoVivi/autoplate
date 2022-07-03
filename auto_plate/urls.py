from django.urls import path

from . import views

urlpatterns = [
    path('', views.CreateNewFileForRecognition.as_view(), name='index'),
]
