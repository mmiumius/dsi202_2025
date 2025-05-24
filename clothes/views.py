# mindvibe_full/clothes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Clothing, Category, HeroBanner
import random
from django.contrib import messages
from django.templatetags.static import static
from django.db.models import Q

from .utils import generate_promptpay_qr_image_data # <--- Import the new function
import base64 # <--- Import base64

# ... (other views like welcome, home, detail, signup_view, login_view, logout_view, etc. remain the same) ...
def welcome(request):
    return render(request, 'clothes/welcome.html')

def home(request):
    query = request.GET.get('q', '')
    items = [] 
    if query:
        items = Clothing.objects.filter(name__icontains=query, available_for_rent=True).order_by('-id')
    else:
        all_items = list(Clothing.objects.filter(available_for_rent=True))
        items_to_display_count = len(all_items) 
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
    return redirect('clothes:welcome')

def products_by_category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    query = request.GET.get('q', '')
    base_query = category.clothes.filter(available_for_rent=True)
    if query:
        clothing_items = base_query.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct().order_by('-created_at')
    else:
        clothing_items = base_query.order_by('-created_at')
    context = {
        'category': category,
        'clothing_items': clothing_items,
        'query': query,
    }
    return render(request, 'clothes/category_products.html', context)

def new_arrivals_view(request):
    items = []
    try:
        items = Clothing.objects.filter(available_for_rent=True).order_by('-created_at')[:4]
    except Exception as e:
        print(f"Error querying Clothing items for New Arrivals: {e}")
        messages.error(request, "เกิดข้อผิดพลาดในการดึงข้อมูลสินค้ามาใหม่")
    context = {
        'page_title': 'New Arrivals',
        'new_arrival_items': items,
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'clothes/new_arrivals_page.html', context)

def popular_rentals_view(request):
    popular_items = []
    try:
        all_items = list(Clothing.objects.filter(available_for_rent=True))
        items_to_display_count = min(len(all_items), 8) 
        popular_items = random.sample(all_items, items_to_display_count) if items_to_display_count > 0 else []
    except Exception as e:
        print(f"Error querying Clothing items for Popular Rentals: {e}")
        messages.error(request, "เกิดข้อผิดพลาดในการดึงข้อมูลสินค้ายอดนิยม")
    context = {
        'page_title': 'Popular Rental',
        'popular_items': popular_items,
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }
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
            'image_url': clothing_item.image.url if clothing_item.image else static('clothes/images/placeholder_product.png'),
            'rental_duration_value': selected_duration_value,
            'rental_duration_text': duration_text_for_cart,
            'size': selected_size,
            'price_per_item': str(actual_price),
            'quantity': 1, # Default quantity to 1 for new item
        }
        if cart_item_key in cart:
             cart[cart_item_key]['quantity'] = cart.get(cart_item_key, {}).get('quantity', 0) + 1
        else:
            cart[cart_item_key] = cart_item_data
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
        del cart[item_key]
        request.session['cart'] = cart
        request.session.modified = True
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
            quantity_val = item_data.get('quantity', 1) # Ensure quantity is considered
            current_price = float(price_str)
            current_quantity = int(quantity_val)
            subtotal += current_price * current_quantity
    except ValueError as e:
        print(f"  VALUE ERROR during subtotal calculation in checkout_view: {e}")
        subtotal = 0 
    except Exception as e:
        print(f"  UNEXPECTED ERROR during subtotal calculation in checkout_view: {e}")
        subtotal = 0

    qr_image_base64 = None
    # --- Generate QR Code for PromptPay ---
    # Replace with your actual PromptPay NID or Mobile
    promptpay_target_account = "0649176150" # Example: Your PromptPay mobile number OR NID
    
    # Determine if target is mobile or NID for the utility function
    target_is_mobile = None
    target_is_nid = None
    if promptpay_target_account and len(promptpay_target_account) == 10 and promptpay_target_account.isdigit():
        target_is_mobile = promptpay_target_account
    elif promptpay_target_account and len(promptpay_target_account) == 13 and promptpay_target_account.isdigit():
        target_is_nid = promptpay_target_account

    if (target_is_mobile or target_is_nid) and subtotal > 0:
        # Generate QR for one-time use with the calculated amount
        qr_bytes = generate_promptpay_qr_image_data(
            mobile=target_is_mobile,
            nid=target_is_nid,
            amount=subtotal,
            one_time=True # Usually for checkouts, QR is one-time
        )
        if qr_bytes:
            qr_image_base64 = base64.b64encode(qr_bytes).decode('utf-8')
            
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'qr_image_base64': qr_image_base64, # Pass QR image data to template
        'promptpay_account': promptpay_target_account # For display
    }
    return render(request, 'clothes/checkout.html', context)

def place_order_view(request):
    if request.method == 'POST':
        # ... (your existing logic for saving order details, contact info, slip, etc.) ...
        
        # For example, getting data from the form:
        # full_name = request.POST.get('full_name')
        # phone_number = request.POST.get('phone_number')
        # email = request.POST.get('email')
        # address = request.POST.get('pickup_notes') # Assuming pickup_notes is address
        # slip_image = request.FILES.get('slip_image')
        # slip_link = request.POST.get('slip_link')
        # payment_notes = request.POST.get('payment_notes')
        
        # Here you would typically:
        # 1. Create an Order object and save it.
        # 2. Create OrderItem objects for each item in the cart and link them to the Order.
        # 3. Handle the slip image/link.
        # 4. Send confirmation emails, etc.

        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        
        messages.success(request, "การสั่งซื้อของคุณสำเร็จแล้ว! ขอบคุณที่ใช้บริการ เราจะติดต่อกลับเพื่อยืนยันเร็วๆ นี้")
        return redirect('clothes:order_thank_you') # Redirect to a thank you page
    else:
        messages.warning(request, "การดำเนินการไม่ถูกต้อง")
        return redirect('clothes:checkout')

def order_thank_you_view(request):
    # You might want to pass order details to this page later
    return render(request, 'clothes/order_thank_you.html')