# mindvibe_full/clothes/admin.py
from django.contrib import admin
from .models import Clothing, Category, HeroBanner # , StyleInspirationImage (ถ้ามี)

@admin.register(Clothing)
class ClothingAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available_for_rent', 'image_preview', 'slug', 'updated_at')
    list_filter = ('available_for_rent', 'category', 'updated_at')
    search_fields = ('name', 'description', 'slug')
    list_editable = ('price', 'available_for_rent', 'category') # เพิ่ม category ให้แก้ไขได้จากหน้า list
    prepopulated_fields = {'slug': ('name',)} # สร้าง slug จาก name อัตโนมัติ
    ordering = ('-updated_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'price')
        }),
        ('Details & Media', { # เปลี่ยนชื่อ Section
            'fields': ('description', 'image', 'available_for_rent')
            # เพิ่มฟิลด์อื่นๆ ที่คุณใส่ใน Model Clothing ที่นี่ เช่น size, color, brand
        }),
        # ('Timestamps', { # Optional: to show read-only timestamps
        #     'fields': ('created_at', 'updated_at'),
        #     'classes': ('collapse',) # ทำให้ซ่อนได้
        # })
    )
    readonly_fields = ('created_at', 'updated_at') # ทำให้ฟิลด์นี้เป็น Read-only ในหน้าแก้ไข

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 60px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'รูปภาพสินค้า'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'image_thumbnail', 'product_count') # เพิ่ม product_count
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def image_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="max-height: 70px; max-width: 100px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_thumbnail.short_description = 'รูปภาพปก'

    def product_count(self, obj): # แสดงจำนวนสินค้าในหมวดหมู่นี้
        return obj.clothes.count() # ใช้ related_name 'clothes' จาก Clothing model
    product_count.short_description = 'จำนวนสินค้า'


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'is_active', 'order', 'image_thumbnail', 'video_link', 'link_url_name', 'updated_at')
    list_filter = ('is_active', 'banner_type')
    search_fields = ('title', 'subtitle')
    list_editable = ('is_active', 'order', 'banner_type')
    ordering = ('order', '-updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'banner_type', 'is_active', 'order')
        }),
        ('Media Content', {
            'fields': ('image', 'video'),
            'description': "ถ้า Banner Type เป็น 'Image Banner' ให้อัปโหลดรูปภาพที่ช่อง 'Image'. ถ้าเป็น 'Video Banner' ให้อัปโหลดไฟล์ที่ช่อง 'Video' และสามารถอัปโหลดรูปที่ช่อง 'Image' เพื่อใช้เป็น Poster ได้ (ไม่บังคับแต่แนะนำ).",
        }),
        ('Link', {
            'fields': ('link_url_name',),
        }),
    )

    def image_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 100px; object-fit: cover;" />', obj.image.url)
        return "No Image/Poster"
    image_thumbnail.short_description = 'รูปภาพ/Poster'

    def video_link(self, obj):
        from django.utils.html import format_html
        if obj.video:
            return format_html('<a href="{}" target="_blank">View Video</a>', obj.video.url)
        return "No Video"
    video_link.short_description = 'ไฟล์ Video'

# (ถ้าคุณมี StyleInspirationImage Model ก็ Register ที่นี่ด้วย)
