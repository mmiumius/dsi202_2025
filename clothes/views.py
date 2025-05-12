# mindvibe_full/clothes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Clothing, Category, HeroBanner
import random
from django.contrib import messages
from django.templatetags.static import static # เพิ่ม import นี้เผื่อใช้ใน image_url fallback

# ... (welcome, home, detail, signup_view, login_view, logout_view functions) ...
def welcome(request):
    return render(request, 'clothes/welcome.html')

def home(request):
    query = request.GET.get('q', '')
    if query:
        items = Clothing.objects.filter(name__icontains=query, available_for_rent=True).order_by('-id')
    else:
        all_items = list(Clothing.objects.filter(available_for_rent=True))
        # items_to_display_count = min(len(all_items), 12) # ตัวอย่าง: แสดง 12 ชิ้น
        items_to_display_count = len(all_items) # แสดงทั้งหมดถ้าไม่จำกัดจำนวน
        items = random.sample(all_items, items_to_display_count) if items_to_display_count > 0 else []


    active_categories = Category.objects.filter(is_active=True).order_by('name')
    active_hero_banner = HeroBanner.objects.filter(is_active=True).order_by('order', '-updated_at').first()

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
            messages.success(request, "สมัครสมาชิกสำเร็จ!")
            return redirect('clothes:home')
        else:
            messages.error(request, "ข้อมูลการสมัครไม่ถูกต้อง กรุณาตรวจสอบ")
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
                messages.info(request, f"ยินดีต้อนรับกลับ, {username}!")
                next_url = request.POST.get('next', None)
                if next_url:
                    return redirect(next_url)
                return redirect('clothes:home')
            else:
                messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    else:
        form = AuthenticationForm()
    next_url = request.GET.get('next', '')
    return render(request, 'clothes/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, "ออกจากระบบเรียบร้อยแล้ว")
    return redirect('clothes:welcome')

def products_by_category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    clothing_items = category.clothes.filter(available_for_rent=True).order_by('-created_at')

    query = request.GET.get('q', '')
    if query:
        clothing_items = clothing_items.filter(name__icontains=query)

    context = {
        'category': category,
        'clothing_items': clothing_items,
        'query': query,
    }
    return render(request, 'clothes/category_products.html', context)

def new_arrivals_view(request):
    items = Clothing.objects.filter(available_for_rent=True).order_by('-created_at')[:12]
    context = {
        'page_title': 'New Arrivals',
        'items': items,
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'clothes/product_list.html', context)

def popular_rentals_view(request):
    all_items = list(Clothing.objects.filter(available_for_rent=True))
    items_to_display_count = min(len(all_items), 12)
    items = random.sample(all_items, items_to_display_count) if items_to_display_count > 0 else []
    context = {
        'page_title': 'Popular Rentals',
        'items': items,
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'clothes/product_list.html', context)


def add_to_cart_view(request, pk):
    clothing_item = get_object_or_404(Clothing, pk=pk)

    if not clothing_item.available_for_rent:
        messages.error(request, f"ขออภัย '{clothing_item.name}' ไม่พร้อมให้เช่าในขณะนี้")
        return redirect('clothes:detail', pk=pk)

    if request.method == 'POST':
        selected_duration_value = request.POST.get('rental_duration')
        selected_size = request.POST.get('selected_size')

        if not selected_duration_value or not selected_size:
            messages.error(request, "ข้อมูลไม่ครบถ้วน กรุณาเลือกแพ็กเกจและไซส์")
            return redirect('clothes:detail', pk=pk)

        actual_price = None
        duration_text_for_cart = ""

        if selected_duration_value == '3_days' and clothing_item.price_3_days is not None:
            actual_price = clothing_item.price_3_days
            duration_text_for_cart = "3 วัน"
        elif selected_duration_value == '5_days' and clothing_item.price_5_days is not None:
            actual_price = clothing_item.price_5_days
            duration_text_for_cart = "5 วัน"
        elif selected_duration_value == '7_days' and clothing_item.price_7_days is not None:
            actual_price = clothing_item.price_7_days
            duration_text_for_cart = "7 วัน"

        if actual_price is None:
            messages.error(request, "แพ็กเกจเช่าที่เลือกไม่ถูกต้องหรือไม่มีราคา")
            return redirect('clothes:detail', pk=pk)

        cart = request.session.get('cart', {})
        cart_item_key = f"{clothing_item.pk}_{selected_duration_value}_{selected_size}"

        cart_item_data = {
            'product_id': clothing_item.pk,
            'name': clothing_item.name,
            'image_url': clothing_item.image.url if clothing_item.image else static('images/default_placeholder.png'), # **แก้ path ของ placeholder ถ้าจำเป็น**
            'rental_duration_value': selected_duration_value,
            'rental_duration_text': duration_text_for_cart,
            'size': selected_size,
            'price_per_item': float(actual_price),
            'quantity': 1,
        }

        if cart_item_key in cart:
             cart[cart_item_key]['quantity'] = cart.get(cart_item_key, {}).get('quantity', 0) + 1
             #messages.info(request, f"อัปเดตจำนวน '{clothing_item.name}' ({duration_text_for_cart}, ไซส์ {selected_size}) ในตะกร้าแล้ว")
        else:
            cart[cart_item_key] = cart_item_data
            # messages.success(request, f"เพิ่ม '{clothing_item.name}' ({duration_text_for_cart}, ไซส์ {selected_size}) ลงในตะกร้าแล้ว!")

        request.session['cart'] = cart
        request.session.modified = True

        return redirect('clothes:cart_detail')

    else:
        messages.warning(request, "การดำเนินการไม่ถูกต้อง")
        return redirect('clothes:detail', pk=pk)


def view_cart(request):
    # --- เพิ่มโค้ดส่วนนี้เข้าไป (ตาม "ข้อ 1" ที่คุยกัน) ---
    cart_data_in_session = request.session.get('cart', {}) # ดึงข้อมูลตะกร้า
    print("\n===================================")
    print("DEBUG: Data in request.session.cart (from view_cart):")
    if cart_data_in_session:
        for key, item_details in cart_data_in_session.items():
            print(f"  Item Key: {key}")
            print(f"    Name: {item_details.get('name')}")
            print(f"    Price: {item_details.get('price_per_item')}")
            print(f"    Quantity: {item_details.get('quantity')}")
            print(f"    Size: {item_details.get('size')}")
            print(f"    Duration: {item_details.get('rental_duration_text')}")
    else:
        print("  Cart is EMPTY in session.")
    print("===================================\n")
    # --- สิ้นสุดส่วนที่เพิ่มเข้าไป ---

    return render(request, 'clothes/cart.html')


def remove_from_cart_view(request, item_key):
    cart = request.session.get('cart', {})

    if item_key in cart:
        removed_item_name = cart[item_key].get('name', 'สินค้า')
        del cart[item_key]
        request.session['cart'] = cart
        request.session.modified = True
        # messages.success(request, f"นำ '{removed_item_name}' ออกจากตะกร้าแล้ว")
    else:
        messages.warning(request, "ไม่พบสินค้านี้ในตะกร้า")

    return redirect('clothes:cart_detail')

# ใน clothes/views.py
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "ตะกร้าสินค้าของคุณว่างเปล่า ไม่สามารถดำเนินการต่อได้")
        return redirect('clothes:cart_detail')

    subtotal = sum(float(item_data.get('price_per_item', 0)) * item_data.get('quantity', 1) for item_data in cart.values())
    context = {
        'cart': cart,
        'subtotal': subtotal
    }
    return render(request, 'clothes/checkout.html', context)

# ใน clothes/views.py

# ... (import อื่นๆ และ views อื่นๆ) ...

def place_order_view(request):
    if request.method == 'POST':
        # 1. ดึงข้อมูลจาก request.POST ที่ส่งมาจากฟอร์ม checkout.html
        #    เช่น full_name, phone_number, email, shipping_address, notes, payment_method
        #    และรายการสินค้าที่เลือก (ถ้าคุณส่งมา) หรือดึงจาก session cart อีกครั้ง
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        shipping_address = request.POST.get('shipping_address', '') # อาจจะไม่มี
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method')

        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "ตะกร้าสินค้าของคุณว่างเปล่า ไม่สามารถสั่งซื้อได้")
            return redirect('clothes:cart_detail')

        # 2. ตรวจสอบความถูกต้องของข้อมูล (Validation)
        #    (เช่น ชื่อต้องไม่ว่าง, เบอร์โทร/อีเมลถูกต้อง)
        if not full_name or not phone_number or not email or not payment_method:
            messages.error(request, "กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน")
            # อาจจะต้อง redirect กลับไปหน้า checkout พร้อมข้อมูลเดิมและ error messages
            # หรือส่ง context ที่มี error กลับไป render หน้า checkout ใหม่
            return redirect('clothes:checkout') # หรือ render หน้า checkout พร้อม error

        # 3. สร้าง Order Object และ OrderItem Objects (ถ้าคุณมี Model สำหรับ Order)
        #    - คำนวณยอดรวมสุดท้าย
        #    - บันทึกข้อมูลลูกค้า, ที่อยู่, รายการสินค้าที่สั่ง, ยอดรวม, สถานะการสั่งซื้อ ฯลฯ
        #    - ตัวอย่าง (สมมติว่าคุณมี Model ชื่อ Order และ OrderItem):
        #
        #    from .models import Order, OrderItem # สมมติว่ามี Model เหล่านี้
        #    order_subtotal = sum(float(item_data.get('price_per_item', 0)) * item_data.get('quantity', 1) for item_data in cart.values())
        #
        #    new_order = Order.objects.create(
        #        user=request.user if request.user.is_authenticated else None, # ถ้าเป็นสมาชิก
        #        full_name=full_name,
        #        phone_number=phone_number,
        #        email=email,
        #        shipping_address=shipping_address,
        #        notes=notes,
        #        payment_method=payment_method,
        #        total_amount=order_subtotal # หรือยอดรวมสุดท้ายจริงๆ
        #        # order_status='pending' หรือ 'processing'
        #    )
        #
        #    for item_key, item_data in cart.items():
        #        clothing_item = Clothing.objects.get(pk=item_data.get('product_id'))
        #        OrderItem.objects.create(
        #            order=new_order,
        #            clothing_item=clothing_item,
        #            quantity=item_data.get('quantity'),
        #            price_at_order=float(item_data.get('price_per_item')),
        #            rental_duration=item_data.get('rental_duration_text'), # หรือ value
        #            size=item_data.get('size')
        #        )

        # 4. อาจจะมีการติดต่อ Payment Gateway (ถ้าใช้)

        # 5. ล้างตะกร้าสินค้าใน session
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True

        #messages.success(request, "การสั่งซื้อของคุณสำเร็จแล้ว! ขอบคุณที่ใช้บริการ")
        # 6. Redirect ไปยังหน้า Thank You หรือหน้าแสดงรายละเอียดการสั่งซื้อ
        return redirect('clothes:order_thank_you') # **สำคัญ:** สร้าง URL และ View ชื่อ 'order_thank_you'
    else:
        # ถ้าไม่ใช่ POST request ให้ redirect กลับไปหน้า checkout
        messages.warning(request, "การดำเนินการไม่ถูกต้อง")
        return redirect('clothes:checkout')
    
def order_thank_you_view(request):
    # คุณอาจจะต้องการดึง Order ID ล่าสุดที่เพิ่งสร้าง (ถ้ามี) มาแสดงผล
    # order_id = request.session.get('last_order_id', None) # ตัวอย่าง
    # context = {'order_id': order_id}
    # if order_id in request.session:
    #     del request.session['last_order_id'] # ลบออกจาก session หลังแสดงผล
    context = {} # ตอนนี้ยังไม่มี context พิเศษ
    return render(request, 'clothes/order_thank_you.html', context)

# ใน clothes/views.py
def new_arrivals_view(request):
    # ... (logic การดึงข้อมูล items) ...
    context = {
        'page_title': 'New Arrivals',
        'items': items,
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }
    # !!! ปัญหาอยู่ที่บรรทัดนี้ Django หา template นี้ไม่เจอ !!!
    return render(request, 'clothes/product_list.html', context)