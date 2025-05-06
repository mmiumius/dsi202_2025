from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout # เพิ่ม logout เข้ามาด้วย
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # ฟอร์มสำเร็จรูปของ Django
from .models import Clothing
import random

def welcome(request):
    return render(request, 'clothes/welcome.html')

def home(request):
    # ถ้าอยากให้หน้านี้เข้าได้เฉพาะคนที่ login แล้ว ให้เพิ่ม @login_required
    # from django.contrib.auth.decorators import login_required
    # @login_required
    query = request.GET.get('q', '')
    if query:
        items = Clothing.objects.filter(name__icontains=query).order_by('-id')
    else:
        all_items = list(Clothing.objects.all())
        items = random.sample(all_items, min(len(all_items), 6))
    return render(request, 'clothes/home.html', {'items': items, 'query': query})

def detail(request, pk):
    # ถ้าอยากให้หน้านี้เข้าได้เฉพาะคนที่ login แล้ว ให้เพิ่ม @login_required
    item = get_object_or_404(Clothing, pk=pk)
    return render(request, 'clothes/detail.html', {'item': item})

# View ใหม่สำหรับหน้าสมัครสมาชิก
def signup_view(request):
    if request.method == 'POST': # ถ้ามีการส่งข้อมูลฟอร์มมา (กดปุ่มสมัคร)
        form = UserCreationForm(request.POST)
        if form.is_valid(): # ตรวจสอบว่าข้อมูลถูกต้องไหม
            user = form.save() # บันทึก user ใหม่
            login(request, user) # ล็อกอิน user คนนี้เข้าระบบเลย
            return redirect('home') # ไปที่หน้า home หลังสมัครเสร็จ
    else: # ถ้าเป็นการเปิดหน้าครั้งแรก (ยังไม่ได้กดปุ่ม)
        form = UserCreationForm() # สร้างฟอร์มเปล่าๆ
    return render(request, 'clothes/signup.html', {'form': form})

# View ใหม่สำหรับหน้าเข้าสู่ระบบ
def login_view(request):
    if request.method == 'POST': # ถ้ามีการส่งข้อมูลฟอร์มมา (กดปุ่มล็อกอิน)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid(): # ตรวจสอบว่าข้อมูลถูกต้องไหม
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password) # ตรวจสอบ user/password
            if user is not None: # ถ้ามี user นี้ในระบบ
                login(request, user) # ล็อกอิน user คนนี้เข้าระบบ
                return redirect('home') # ไปที่หน้า home หลังล็อกอินเสร็จ
            else:
                # กรณีล็อกอินไม่ผ่าน อาจจะแสดงข้อความผิดพลาด
                pass
    else: # ถ้าเป็นการเปิดหน้าครั้งแรก
        form = AuthenticationForm() # สร้างฟอร์มเปล่าๆ
    return render(request, 'clothes/login.html', {'form': form})

# View ใหม่สำหรับ Logout
def logout_view(request):
    logout(request) # สั่งให้ user ออกจากระบบ
    return redirect('welcome') # กลับไปที่หน้า welcome

def get_or_create_cart(request):
    """Helper function เพื่อดึงหรือสร้าง Cart สำหรับ session ปัจจุบัน"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create() # สร้าง session ถ้ายังไม่มี
        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)
    # อาจจะเพิ่ม logic ผูกกับ User ถ้า login อยู่ด้วยก็ได้
    # if request.user.is_authenticated:
    #     cart.user = request.user
    #     cart.save()
    return cart

def add_to_cart(request, pk):
    clothing_item = get_object_or_404(Clothing, pk=pk, available=True) # เช็คว่าสินค้ามีอยู่และ available
    cart = get_or_create_cart(request)

    # ตรวจสอบว่ามีสินค้านี้ในตะกร้าแล้วหรือยัง
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        clothing=clothing_item,
        defaults={'quantity': 1} # ถ้าสร้างใหม่ ให้ quantity เป็น 1
    )

    if not created:
        # ถ้ามีอยู่แล้ว ให้เพิ่ม quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"เพิ่มจำนวน '{clothing_item.name}' ในตะกร้าแล้ว!")
    else:
        messages.success(request, f"เพิ่ม '{clothing_item.name}' ลงในตะกร้าแล้ว!")

    # Redirect กลับไปหน้าเดิม หรือหน้า detail หรือหน้าตะกร้า
    # ตอนนี้ redirect กลับไปหน้า detail ก่อน
    return redirect('detail', pk=pk)
# --- จบ Add to Cart View ---

# อย่าลืม import get_or_create_cart และ add_to_cart ใน __init__.py ของ app ถ้าจำเป็น
# หรือ ensure ว่ามันถูก include อย่างถูกต้องใน urls.py