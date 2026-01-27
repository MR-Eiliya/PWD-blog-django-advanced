from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path('', name="index"),
    path('about', name="about"),
    path('contact', name="contact"),
]