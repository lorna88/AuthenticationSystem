from django.urls import path

from .views import RegisterUserView, UserProfileView

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]