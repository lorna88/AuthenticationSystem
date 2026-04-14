from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('permissions/', include('permissions.urls', namespace='permissions')),
    path('authentication/', include('authentication.urls', namespace='authentication')),
    path('mock/', include('business_mock.urls', namespace='mock')),
]
