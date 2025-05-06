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