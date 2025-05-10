# mindvibe_full/clothes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Clothing, Category # <<<--- เพิ่ม Category เข้ามา
# from .models import Cart, CartItem # ถ้าจะใช้ Cart
# from django.contrib import messages # ถ้าจะใช้ messages
import random

def welcome(request):
    return render(request, 'clothes/welcome.html')

def home(request):
    query = request.GET.get('q', '')
    if query:
        items = Clothing.objects.filter(name__icontains=query, available=True).order_by('-id') # กรองเฉพาะ available=True
    else:
        all_items = list(Clothing.objects.filter(available=True)) # กรองเฉพาะ available=True
        # สุ่มแสดงสินค้า ถ้ามีน้อยกว่า 6 ก็แสดงทั้งหมด
        items_to_display_count = min(len(all_items), 6) # แก้ไขเพื่อให้สุ่มไม่เกินจำนวนสินค้าที่มี
        items = random.sample(all_items, items_to_display_count) if items_to_display_count > 0 else []


    # ดึงข้อมูล Categories ที่ is_active = True
    active_categories = Category.objects.filter(is_active=True).order_by('name')

    context = {
        'items': items, # สินค้า (อาจจะเปลี่ยนเป็น New Arrivals หรือ Popular Rentals ทีหลัง)
        'query': query,
        'categories': active_categories, # <<<--- ส่ง categories ไปยัง template
        # 'hero_image_url': '/media/hero_images/your_hero_image.jpg', # ตัวอย่างถ้าจะส่ง URL รูป Hero
    }
    return render(request, 'clothes/home.html', context)

# ... (ส่วนที่เหลือของ views.py เหมือนเดิม) ...
# Detail view
def detail(request, pk):
    item = get_object_or_404(Clothing, pk=pk)
    return render(request, 'clothes/detail.html', {'item': item})

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('clothes:home') # ใช้ namespace
    else:
        form = UserCreationForm()
    return render(request, 'clothes/signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('clothes:home') # ใช้ namespace
    else:
        form = AuthenticationForm()
    return render(request, 'clothes/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('clothes:welcome') # ใช้ namespace

def get_or_create_cart(request):
    """Helper function เพื่อดึงหรือสร้าง Cart สำหรับ session ปัจจุบัน"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create() # สร้าง session ถ้ายังไม่มี
        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)
    # อาจจะเพิ่ม logic ผูกกับ User ถ้า login อยู่ด้วยก็ได้
    # if request.user.is_authenticated:
    #     cart.user = request.user # ต้องเพิ่ม field user ใน Cart model ด้วย
    #     cart.save()
    return cart

def add_to_cart(request, pk):
    clothing_item = get_object_or_404(Clothing, pk=pk, available=True)
    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        clothing=clothing_item,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"เพิ่มจำนวน '{clothing_item.name}' ในตะกร้าแล้ว!")
    else:
        messages.success(request, f"เพิ่ม '{clothing_item.name}' ลงในตะกร้าแล้ว!")

    # ควรจะ redirect ไปที่หน้ารายละเอียดสินค้า หรือหน้าตะกร้าสินค้า
    return redirect('clothes:detail', pk=pk) # redirect กลับไปหน้า detail