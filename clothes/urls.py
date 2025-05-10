# mindvibe_full/clothes/urls.py
from django.urls import path
from . import views

app_name = 'clothes'  # <<<--- เพิ่ม/ตรวจสอบบรรทัดนี้

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('clothing/<int:pk>/', views.detail, name='detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'), # ยัง comment ไว้อยู่

    # เพิ่ม URL patterns ชั่วคราว (ชี้ไปที่ home view ก่อน)
    # คุณจะต้องสร้าง View ที่เหมาะสมสำหรับ URL เหล่านี้ในภายหลัง
    path('new-arrivals/', views.home, name='new_arrivals'),
    path('popular-rentals/', views.home, name='popular_rentals'),
    # ถ้า Category model ของคุณใช้ get_absolute_url ที่ reverse ไปที่ 'products_by_category'
    # ให้ un-comment บรรทัดด้านล่าง และตรวจสอบว่า Category model มี get_absolute_url ที่ถูกต้อง
    # path('category/<slug:category_slug>/', views.home, name='products_by_category'),
]