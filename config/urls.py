from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/manage/', include('permissions.urls', namespace='permissions')),
    path('api/auth/', include('authentication.urls', namespace='authentication')),
    path('api/mock/', include('business_mock.urls', namespace='mock')),
]
