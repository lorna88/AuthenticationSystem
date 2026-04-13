from django.urls import path

from .views import RegisterUserView, UserProfileView, UserManagementView

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('my_profile/', UserProfileView.as_view(), name='my_profile'),
    path('users/', UserManagementView.as_view(), name='users'),
]