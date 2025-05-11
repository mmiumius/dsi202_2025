# mindvibe_full/clothes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Clothing, Category, HeroBanner
import random

# ... (welcome, home, detail, signup_view, login_view, logout_view functions) ...
def welcome(request):
    return render(request, 'clothes/welcome.html')

def home(request):
    query = request.GET.get('q', '')
    if query:
        items = Clothing.objects.filter(name__icontains=query, available_for_rent=True).order_by('-id') # แก้เป็น available_for_rent
    else:
        all_items = list(Clothing.objects.filter(available_for_rent=True)) # แก้เป็น available_for_rent
        items_to_display_count = min(len(all_items), 0)
        items = random.sample(all_items, items_to_display_count) if items_to_display_count > 0 else []

    active_categories = Category.objects.filter(is_active=True).order_by('name')
    active_hero_banner = HeroBanner.objects.filter(is_active=True).order_by('order', '-updated_at').first()

    # --- DEBUGGING PRINTS START ---
    print("\n--- Debugging Categories in home view ---")
    if active_categories.exists():
        print(f"Found {active_categories.count()} active categories.")
        for cat in active_categories:
            print(f"Category: {cat.name}")
            if cat.image:
                print(f"  Image exists: {cat.image.name}")
                print(f"  Image URL: {cat.image.url}")
            else:
                print(f"  Image field is EMPTY for {cat.name}.")
    else:
        print("NO active categories found in the database.")
    print("--- End Debugging Categories ---\n")

    print("--- Debugging Hero Banner in home view ---")
    if active_hero_banner:
        print(f"Found active_hero_banner: {active_hero_banner.title}")
        if active_hero_banner.image:
            print(f"Hero Banner Image exists: {active_hero_banner.image.name}")
            print(f"Hero Banner Image URL: {active_hero_banner.image.url}")
        else:
            print("Hero Banner Image field is EMPTY.")

        if hasattr(active_hero_banner, 'banner_type'):
            print(f"Hero Banner Type (raw): {active_hero_banner.banner_type}")
            if hasattr(active_hero_banner, 'get_banner_type_display'):
                print(f"Hero Banner Type (display): {active_hero_banner.get_banner_type_display()}")
            else:
                print("Hero Banner object does NOT have get_banner_type_display method.")
        else:
            print("Hero Banner object does NOT have banner_type attribute (check models.py and migrations).")

        if hasattr(active_hero_banner, 'banner_type') and active_hero_banner.banner_type == 'video':
            if active_hero_banner.video:
                 print(f"Hero Banner Video exists: {active_hero_banner.video.name}")
                 print(f"Hero Banner Video URL: {active_hero_banner.video.url}")
            else:
                print("Hero Banner Video field is EMPTY (but type is video).")
    else:
        print("NO active_hero_banner found in the database (check 'is_active' in admin).")
    print("--- End Debugging Hero Banner ---\n")
    # --- DEBUGGING PRINTS END ---

    context = {
        'items': items,
        'query': query,
        'categories': active_categories,
        'hero_banner': active_hero_banner,
    }
    return render(request, 'clothes/home.html', context)

def detail(request, pk):
    item = get_object_or_404(Clothing, pk=pk)
    return render(request, 'clothes/detail.html', {'item': item})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('clothes:home')
    else:
        form = UserCreationForm()
    return render(request, 'clothes/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('clothes:home')
    else:
        form = AuthenticationForm()
    return render(request, 'clothes/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('clothes:welcome')

# --- START NEW VIEW FUNCTION ---
def products_by_category_view(request, category_slug):
    # ดึง Category object จาก slug ที่ได้รับมา, ถ้าไม่เจอจะแสดง 404 error
    category = get_object_or_404(Category, slug=category_slug, is_active=True)

    # ดึงสินค้าทั้งหมดที่อยู่ใน Category นี้ และ available_for_rent = True
    # clothing_items = Clothing.objects.filter(category=category, available_for_rent=True).order_by('-created_at')
    # หรือถ้าคุณใช้ related_name='clothes' ใน ForeignKey ของ Clothing model:
    clothing_items = category.clothes.filter(available_for_rent=True).order_by('-created_at')


    # (ส่วน Search จะเพิ่มทีหลัง)
    query = request.GET.get('q', '')
    if query:
        clothing_items = clothing_items.filter(name__icontains=query) # ค้นหาเฉพาะในหมวดหมู่นี้

    context = {
        'category': category,
        'clothing_items': clothing_items,
        'query': query,
    }
    # เราจะต้องสร้าง template ใหม่สำหรับหน้านี้ เช่น 'clothes/category_products.html'
    return render(request, 'clothes/category_products.html', context)
# --- END NEW VIEW FUNCTION ---

# --- START PLACEHOLDER VIEWS for new_arrivals and popular_rentals ---
def new_arrivals_view(request):
    # TODO: Implement logic to get new arrival items
    # For now, let's just reuse the home context but maybe with a different title or filter
    items = Clothing.objects.filter(available_for_rent=True).order_by('-created_at')[:12] # เอา 12 ชิ้นล่าสุด
    context = {
        'page_title': 'New Arrivals',
        'items': items,
        'categories': Category.objects.filter(is_active=True).order_by('name'), # ส่ง categories ไปด้วยเผื่อใช้ใน navbar
    }
    # เราจะต้องสร้าง template ใหม่สำหรับหน้านี้ เช่น 'clothes/product_list.html'
    # หรือจะใช้ template กลางสำหรับแสดงรายการสินค้าก็ได้
    return render(request, 'clothes/product_list.html', context)

def popular_rentals_view(request):
    # TODO: Implement logic to get popular rental items (e.g., based on rental count or views)
    # For now, let's just reuse the home context or show some random items
    all_items = list(Clothing.objects.filter(available_for_rent=True))
    items_to_display_count = min(len(all_items), 12) # แสดง 12 ชิ้น
    items = random.sample(all_items, items_to_display_count) if items_to_display_count > 0 else []
    context = {
        'page_title': 'Popular Rentals',
        'items': items,
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'clothes/product_list.html', context)
# --- END PLACEHOLDER VIEWS ---


# --- START CART VIEWS (ถ้าคุณจะเปิดใช้งาน) ---
# from .models import Cart, CartItem # ตรวจสอบว่า import ถูกต้อง
# from django.contrib import messages

# def get_or_create_cart(request):
#     session_key = request.session.session_key
#     if not session_key:
#         request.session.create()
#         session_key = request.session.session_key
#     cart, created = Cart.objects.get_or_create(session_key=session_key)
#     return cart

# def add_to_cart(request, pk):
#     clothing_item = get_object_or_404(Clothing, pk=pk, available_for_rent=True)
#     cart = get_or_create_cart(request)
#     cart_item, created = CartItem.objects.get_or_create(
#         cart=cart,
#         clothing=clothing_item,
#         defaults={'quantity': 1}
#     )
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()
#         messages.success(request, f"Updated quantity of '{clothing_item.name}' in your cart.")
#     else:
#         messages.success(request, f"Added '{clothing_item.name}' to your cart.")
#     return redirect('clothes:detail', pk=pk)

# def view_cart(request):
#     cart = get_or_create_cart(request)
#     cart_items = cart.items.all()
#     total_cart_price = sum(item.total_price for item in cart_items if hasattr(item.clothing, 'price') and item.clothing.price is not None)
#     context = {
#         'cart_items': cart_items,
#         'total_cart_price': total_cart_price,
#     }
#     return render(request, 'clothes/cart_view.html', context) # สร้าง template นี้ด้วย

# def remove_from_cart(request, item_id):
#     cart_item = get_object_or_404(CartItem, id=item_id)
#     # อาจจะเพิ่มการตรวจสอบว่าเป็นของ session ปัจจุบันหรือไม่
#     cart_item.delete()
#     messages.success(request, f"Removed '{cart_item.clothing.name}' from your cart.")
#     return redirect('clothes:view_cart')
# --- END CART VIEWS ---