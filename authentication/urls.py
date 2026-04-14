from django.urls import path

from .views import RegisterUserView, UserProfileView, UserManagementView, LoginView, LogoutView

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('my_profile/', UserProfileView.as_view(), name='my_profile'),
    path('users/', UserManagementView.as_view(), name='users'),
    path('users/<int:pk>/', UserManagementView.as_view(), name='user_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]