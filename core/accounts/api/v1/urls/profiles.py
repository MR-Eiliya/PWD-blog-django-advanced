from django.urls import path, include
from .. import views


urlpatterns = [
    # Profile
    path("", views.ProfileAPIView.as_view(), name="profile")
]
