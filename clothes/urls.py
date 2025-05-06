from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('clothing/<int:pk>/', views.detail, name='detail'),
    path('signup/', views.signup_view, name='signup'),    # URL ใหม่สำหรับหน้าสมัครสมาชิก
    path('login/', views.login_view, name='login'),      # URL ใหม่สำหรับหน้าเข้าสู่ระบบ
    path('logout/', views.logout_view, name='logout'),    # URL ใหม่สำหรับออกจากระบบ
]