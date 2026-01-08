from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home, login, signup
    path('', include('accounts.urls')),

    # Dashboard module
    path('dashboard/', include('dashboard.urls')),
]
