from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path("", views.homepage, name="homepage"),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]


