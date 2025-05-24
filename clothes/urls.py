# mindvibe_full/clothes/urls.py
from django.urls import path
from . import views

app_name = 'clothes'

urlpatterns = [
    # หน้าแรกสุด (Welcome Page)
    path('', views.welcome, name='welcome'),

    # หน้าหลักของร้านค้า (แสดง Hero Banner, Categories, etc.)
    path('home/', views.home, name='home'),

    # หน้ารายละเอียดสินค้า (ตาม Primary Key)
    path('clothing/<int:pk>/', views.detail, name='detail'),

    # หน้าสำหรับ User Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # URL สำหรับหน้ารายการสินค้าตาม Category (ใช้ slug ของ category)
    path('category/<slug:category_slug>/', views.products_by_category_view, name='products_by_category'),

    # URL สำหรับ New Arrivals และ Popular Rentals
    path('new-arrivals/', views.new_arrivals_view, name='new_arrivals'),
    path('popular-rentals/', views.popular_rentals_view, name='popular_rentals'),

    # URL สำหรับ Cart
    path('cart/add/<int:pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart_detail'),
    path('cart/remove/<str:item_key>/', views.remove_from_cart_view, name='cart_remove_item'), # อันนี้มีแล้ว ถูกต้อง

    # URL สำหรับ Checkout
    path('checkout/', views.checkout_view, name='checkout'), # อันนี้มีแล้ว ถูกต้อง

    # !!! เพิ่ม path สำหรับการยืนยันการสั่งซื้อ (Place Order) !!!
    path('order/place/', views.place_order_view, name='place_order'),

    # !!! (แนะนำ) เพิ่ม path สำหรับหน้า Thank You (ตัวอย่าง) !!!
    # คุณจะต้องสร้าง view 'order_thank_you_view' และ template สำหรับหน้านี้ด้วย
    path('order/thank-you/', views.order_thank_you_view, name='order_thank_you'),

    path('new-arrivals/', views.new_arrivals_view, name='new_arrivals'),

]