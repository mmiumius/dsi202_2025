# mindvibe_full/clothes/urls.py
from django.urls import path
from . import views

app_name = 'clothes'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('clothing/<int:pk>/', views.detail, name='detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # URL สำหรับหน้ารายการสินค้าตาม Category
    path('category/<slug:category_slug>/', views.products_by_category_view, name='products_by_category'),

    # URL สำหรับ New Arrivals และ Popular Rentals
    path('new-arrivals/', views.new_arrivals_view, name='new_arrivals'),
    path('popular-rentals/', views.popular_rentals_view, name='popular_rentals'),

    # URL สำหรับตะกร้าสินค้า (ถ้าจะเปิดใช้งาน)
    # path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    # path('cart/view/', views.view_cart, name='view_cart'),
    # path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]