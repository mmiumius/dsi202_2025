# mindvibe_full/clothes/admin.py
from django.contrib import admin
from .models import Clothing, Category # เพิ่ม Category เข้ามา

@admin.register(Clothing) # หรือ admin.site.register(Clothing, ClothingAdmin) ถ้ามี ClothingAdmin
class ClothingAdmin(admin.ModelAdmin):
    list_display = ('name', 'available', 'image_preview') # เพิ่ม image_preview
    list_filter = ('available',)
    search_fields = ('name',)

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'image_thumbnail') # ฟิลด์ที่แสดงใน Admin list
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # สร้าง slug จาก name อัตโนมัติ
    ordering = ('name',)

    def image_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.image:
            # ทำให้ thumbnail มีขนาดใหญ่ขึ้นเล็กน้อยเพื่อให้เห็นรายละเอียดรูป Cover ชัดขึ้น
            return format_html('<img src="{}" style="max-height: 70px; max-width: 100px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_thumbnail.short_description = 'รูปภาพปก'

# ถ้าคุณไม่ได้ใช้ @admin.register สามารถทำแบบนี้แทน:
# admin.site.register(Clothing, ClothingAdmin) # ถ้ามี ClothingAdmin
# admin.site.register(Category, CategoryAdmin)

