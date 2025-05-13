# mindvibe_full/clothes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Clothing, Category, HeroBanner # ตรวจสอบว่า import Clothing, Category, HeroBanner ถูกต้อง
import random
from django.contrib import messages
from django.templatetags.static import static # เพิ่ม import นี้เผื่อใช้ใน image_url fallback

def welcome(request):
    return render(request, 'clothes/welcome.html')

def home(request):
    query = request.GET.get('q', '')
    items = [] # กำหนดค่าเริ่มต้นให้ items เป็น list ว่าง
    if query:
        items = Clothing.objects.filter(name__icontains=query, available_for_rent=True).order_by('-id')
    else:
        all_items = list(Clothing.objects.filter(available_for_rent=True))
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
    clothing_items = [] # กำหนดค่าเริ่มต้น
    try:
        clothing_items = category.clothes.filter(available_for_rent=True).order_by('-created_at')
        query = request.GET.get('q', '')
        if query:
            clothing_items = clothing_items.filter(name__icontains=query)
    except Exception as e:
        print(f"Error in products_by_category_view for category '{category_slug}': {e}")
        messages.error(request, "เกิดข้อผิดพลาดในการดึงข้อมูลสินค้าสำหรับหมวดหมู่นี้")

    context = {
        'category': category,
        'clothing_items': clothing_items,
        'query': query if 'query' in locals() else '', # Ensure query is in context
    }
    return render(request, 'clothes/category_products.html', context)

# ใน clothes/views.py

def new_arrivals_view(request):
    items = []
    try:
        # Logic การดึงสินค้า New Arrivals (เช่น 12 ชิ้นล่าสุด)
        items = Clothing.objects.filter(available_for_rent=True).order_by('-created_at')[:4]
    except Exception as e:
        print(f"Error querying Clothing items for New Arrivals: {e}")
        messages.error(request, "เกิดข้อผิดพลาดในการดึงข้อมูลสินค้ามาใหม่")

    context = {
        'page_title': 'New Arrivals', # เปลี่ยน title ได้ตามต้องการ
        'new_arrival_items': items,    # เปลี่ยนชื่อ key ใน context ถ้าต้องการ (แล้วใน template ใหม่ก็ต้องใช้ชื่อนี้)
        'categories': Category.objects.filter(is_active=True).order_by('name'), # อาจจะยังส่งไปเผื่อใช้ใน navbar
    }
    # !!! เปลี่ยนชื่อ template ที่จะ render ตรงนี้ !!!
    return render(request, 'clothes/new_arrivals_page.html', context)

# ใน clothes/views.py

def popular_rentals_view(request):
    popular_items = []
    try:
        # ตัวอย่าง: ดึงสินค้า 10 อันดับแรกที่ถูกเช่ามากที่สุด (สมมติว่ามี field 'rental_count')
        # คุณต้องเพิ่ม field 'rental_count' ใน Model Clothing และมี logic การนับด้วยนะครับ
        # popular_items = Clothing.objects.filter(available_for_rent=True).order_by('-rental_count')[:10]

        # หรือถ้ายังไม่มี rental_count ก็ยังคงใช้ random sample ไปก่อน หรือเลือกแบบอื่น
        all_items = list(Clothing.objects.filter(available_for_rent=True))
        items_to_display_count = min(len(all_items), 8) # แสดง 8 ชิ้น
        popular_items = random.sample(all_items, items_to_display_count) if items_to_display_count > 0 else []
        # ถ้าจะให้ดี ควรจะมี logic ที่ดีกว่า random สำหรับ "Popular"
    except Exception as e:
        print(f"Error querying Clothing items for Popular Rentals: {e}")
        messages.error(request, "เกิดข้อผิดพลาดในการดึงข้อมูลสินค้ายอดนิยม")

    context = {
        'page_title': 'Popular Rental', # เปลี่ยน title
        'popular_items': popular_items,    # เปลี่ยนชื่อ key ใน context
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }
    # !!! เปลี่ยนชื่อ template ที่จะ render ตรงนี้ !!!
    return render(request, 'clothes/popular_rentals_page.html', context)

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
            'image_url': clothing_item.image.url if clothing_item.image else static('clothes/images/placeholder_product.png'), # ใช้ clothes/images/
            'rental_duration_value': selected_duration_value,
            'rental_duration_text': duration_text_for_cart,
            'size': selected_size,
            'price_per_item': str(actual_price),
            'quantity': 1,
        }
        if cart_item_key in cart:
             cart[cart_item_key]['quantity'] = cart.get(cart_item_key, {}).get('quantity', 0) + 1
             # messages.info(request, f"อัปเดตจำนวน '{clothing_item.name}' ({duration_text_for_cart}, ไซส์ {selected_size}) ในตะกร้าแล้ว")
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

def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "ตะกร้าสินค้าของคุณว่างเปล่า ไม่สามารถดำเนินการต่อได้")
        return redirect('clothes:cart_detail')
    subtotal = 0
    try:
        for item_data in cart.values():
            price_str = item_data.get('price_per_item', '0')
            quantity_val = item_data.get('quantity', 1)
            current_price = float(price_str)
            current_quantity = int(quantity_val)
            subtotal += current_price * current_quantity
    except ValueError as e:
        print(f"  VALUE ERROR during subtotal calculation in checkout_view: {e}")
        subtotal = 0
    except Exception as e:
        print(f"  UNEXPECTED ERROR during subtotal calculation in checkout_view: {e}")
        subtotal = 0
    context = {
        'cart': cart,
        'subtotal': subtotal
    }
    return render(request, 'clothes/checkout.html', context)

def place_order_view(request):
    if request.method == 'POST':
        # ... (logic การดึงข้อมูลจาก form และบันทึก order) ...
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        # messages.success(request, "การสั่งซื้อของคุณสำเร็จแล้ว! ขอบคุณที่ใช้บริการ")
        return redirect('clothes:order_thank_you')
    else:
        messages.warning(request, "การดำเนินการไม่ถูกต้อง")
        return redirect('clothes:checkout')

def order_thank_you_view(request):
    return render(request, 'clothes/order_thank_you.html')