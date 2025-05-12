from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
import os
from django.utils.text import slugify
from django.utils import timezone  # เพิ่ม import นี้

# Function to validate video file extension (ถ้ายังไม่ได้ย้ายมาไว้บนสุด ให้ย้ายมาครับ)
def validate_video_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.mp4', '.webm', '.ogg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension for video. Allowed: .mp4, .webm, .ogg')

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="ชื่อหมวดหมู่ (เช่น Evening Gowns, Casual Chic)")
    slug = models.SlugField(max_length=120, unique=True, help_text="ส่วนที่แสดงใน URL (ภาษาอังกฤษ, ไม่มีเว้นวรรค, ตัวเล็ก)")
    image = models.ImageField(
        upload_to='category_covers/',
        blank=True,
        null=True,
        help_text="รูปภาพหน้าปกของหมวดหมู่"
    )
    description = models.TextField(blank=True, null=True, help_text="คำอธิบายสั้นๆ (ถ้ามี)")
    is_active = models.BooleanField(default=True, help_text="แสดงหมวดหมู่นี้บนเว็บไซต์หรือไม่?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "หมวดหมู่สินค้า"
        verbose_name_plural = "หมวดหมู่สินค้า"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        try:
            return reverse('clothes:products_by_category', kwargs={'category_slug': self.slug})
        except Exception as e:
            print(f"Warning in Category.get_absolute_url: Could not reverse URL for category '{self.slug}'. URL 'clothes:products_by_category' might be missing or incorrect. Error: {e}")
            try:
                return reverse('clothes:home')  # Fallback to home
            except:
                return "#"  # Ultimate fallback

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug

            # Check for uniqueness in Category
            if self.__class__ == Category:
                queryset = Category.objects.filter(slug=self.slug)
            else:
                queryset = Clothing.objects.filter(slug=self.slug)
            
            # If there's a conflict, append a counter
            counter = 1
            while queryset.exists():
                self.slug = f"{original_slug}-{counter}"
                if self.__class__ == Category:
                    queryset = Category.objects.filter(slug=self.slug)
                else:
                    queryset = Clothing.objects.filter(slug=self.slug)
                counter += 1

        super().save(*args, **kwargs)

class Clothing(models.Model):
    category = models.ForeignKey(
        'Category',
        related_name='clothes',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="เลือกหมวดหมู่สำหรับชุดนี้"
    )
    name = models.CharField(max_length=100, help_text="ชื่อชุด")
    slug = models.SlugField(max_length=120, unique=True, blank=True, help_text="URL (สร้างจากชื่ออัตโนมัติ)")
    description = models.TextField(help_text="รายละเอียดชุด, เนื้อผ้า, คำแนะนำในการเช่า (ถ้ามี)")
    image = models.ImageField(upload_to='clothing_images/', help_text="รูปภาพหลักของชุด")

    # ✅ ราคาเช่า 3, 5, 7 วัน
    price_3_days = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="ราคาเช่า 3 วัน (บาท)")
    price_5_days = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="ราคาเช่า 5 วัน (บาท)")
    price_7_days = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="ราคาเช่า 7 วัน (บาท)")

    available_for_rent = models.BooleanField(default=True, help_text="ชุดนี้พร้อมให้เช่าหรือไม่?")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "สินค้าเสื้อผ้า"
        verbose_name_plural = "สินค้าเสื้อผ้า"
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        try:
            return reverse('clothes:detail', kwargs={'pk': self.pk})
        except Exception as e:
            print(f"Warning in Clothing.get_absolute_url: {e}")
            return "#"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            queryset = Clothing.objects.filter(slug=self.slug)
            counter = 1
            while queryset.exists():
                self.slug = f"{original_slug}-{counter}"
                queryset = Clothing.objects.filter(slug=self.slug)
                counter += 1
        super().save(*args, **kwargs)


class HeroBanner(models.Model):
    title = models.CharField(max_length=200, help_text="หัวข้อหลักบน Banner")
    subtitle = models.TextField(blank=True, null=True, help_text="คำโปรยหรือข้อความย่อย")
    BANNER_TYPE_CHOICES = [
        ('image', 'Image Banner'),
        ('video', 'Video Banner'),
    ]
    banner_type = models.CharField(
        max_length=10,
        choices=BANNER_TYPE_CHOICES,
        default='image',
        help_text="เลือกประเภทของ Banner"
    )
    image = models.ImageField(
        upload_to='hero_banners/images/',
        blank=True,
        null=True,
        help_text="รูปภาพปก (สำหรับ Image Banner หรือ Poster ของ Video)"
    )
    video = models.FileField(
        upload_to='hero_banners/videos/',
        blank=True,
        null=True,
        validators=[validate_video_extension],
        help_text="ไฟล์ Video (แนะนำ .mp4, .webm, .ogg)"
    )
    link_url_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="ชื่อ URL pattern ที่จะให้ Banner นี้ลิงก์ไป (เช่น clothes:new_arrivals)"
    )
    is_active = models.BooleanField(default=False, help_text="เลือก True เพื่อให้ Banner นี้แสดงผล")
    order = models.PositiveIntegerField(default=0, help_text="ลำดับการแสดงผล")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hero Banner"
        verbose_name_plural = "Hero Banners"
        ordering = ['order', '-created_at']

    def __str__(self):
        if hasattr(self, 'get_banner_type_display'):
            return f"{self.title} ({self.get_banner_type_display()})"
        return self.title

    def get_link_url(self):
        if self.link_url_name:
            try:
                if ':' in self.link_url_name:
                    return reverse(self.link_url_name)
                else:
                    return reverse(f'clothes:{self.link_url_name}')
            except Exception as e:
                print(f"Error reversing URL '{self.link_url_name}': {e}")
                return "#"
        return "#"

    def clean(self):
        super().clean()
        if self.banner_type == 'image' and not self.image:
            raise ValidationError({'image': 'กรุณาอัปโหลดรูปภาพสำหรับ Image Banner'})
        if self.banner_type == 'video' and not self.video:
            raise ValidationError({'video': 'กรุณาอัปโหลดไฟล์ Video สำหรับ Video Banner'})

class Cart(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart (Session: {self.session_key})" if self.session_key else f"Cart (ID: {self.id})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    clothing = models.ForeignKey(Clothing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.clothing.name} in {self.cart}"

    @property
    def total_price(self):
        if hasattr(self.clothing, 'price') and self.clothing.price is not None:
            return self.clothing.price * self.quantity
        return 0

# (ถ้าคุณมี StyleInspirationImage Model ก็ใส่ต่อจากตรงนี้)
