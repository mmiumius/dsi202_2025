from django.db import models

class Clothing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='clothes/')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    # อาจจะผูกกับ User หรือใช้ session_key
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True) # สำหรับ user ที่ยังไม่ login
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # if self.user:
        #     return f"Cart for {self.user.username}"
        return f"Cart (Session: {self.session_key})" if self.session_key else f"Cart (ID: {self.id})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    clothing = models.ForeignKey(Clothing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.clothing.name} in {self.cart}"

    # เพิ่ม property เพื่อคำนวณราคารวมของ item นี้
    @property
    def total_price(self):
        return self.clothing.price * self.quantity

# -------------------------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="ชื่อหมวดหมู่ (เช่น Evening Gowns, Casual Chic)")
    slug = models.SlugField(max_length=120, unique=True, help_text="ส่วนที่แสดงใน URL (ภาษาอังกฤษ, ไม่มีเว้นวรรค, ตัวเล็ก)")
    image = models.ImageField(
        upload_to='category_covers/',
        blank=True,
        null=True,
        help_text="รูปภาพหน้าปกของหมวดหมู่ (ควรมีขนาดเหมาะสมสำหรับแสดงผลเป็น Cover)"
    )
    description = models.TextField(blank=True, null=True, help_text="คำอธิบายสั้นๆ (ถ้ามี)")
    is_active = models.BooleanField(default=True, help_text="แสดงหมวดหมู่นี้บนเว็บไซต์หรือไม่?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "หมวดหมู่ (Category)"
        verbose_name_plural = "หมวดหมู่ (Categories)"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # แก้ไขให้ใช้ namespace 'clothes'
        # ถ้าคุณมี URL pattern ชื่อ 'products_by_category' ใน clothes/urls.py
        # ที่รับ category_slug เป็น argument
        # ตรวจสอบให้แน่ใจว่าคุณได้ un-comment path สำหรับ 'products_by_category' ใน clothes/urls.py ด้วย
        try:
            return reverse('clothes:products_by_category', kwargs={'category_slug': self.slug})
        except: # ถ้ายังไม่มี URL pattern นั้น หรือมีปัญหาในการ reverse ก็ให้ return # ไปก่อน
            return "#"