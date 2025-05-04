from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('clothing/<int:pk>/', views.detail, name='detail'),
]
