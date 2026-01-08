from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('food/', views.food, name='food'),
    path('electricity/', views.electricity, name='electricity'),
    path('travel/', views.travel, name='travel'),
    path('waste/', views.waste, name='waste'),
    path("summary/", views.carbon_summary, name="carbon_summary"),
    path("scan-waste/", views.scan_waste, name="scan_waste"),

    path("carbon-advisor/", views.carbon_advisor, name="carbon_advisor"),
    path("carbon-advisor/chat/", views.carbon_advisor_chat, name="carbon_advisor_chat"),
]
