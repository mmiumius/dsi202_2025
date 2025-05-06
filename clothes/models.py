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
