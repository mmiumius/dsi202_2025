# Generated by Django 5.1.6 on 2025-05-11 12:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clothes", "0003_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="HeroBanner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="หัวข้อหลักบน Banner (เช่น Find Your Next Vibe)",
                        max_length=200,
                    ),
                ),
                (
                    "subtitle",
                    models.TextField(
                        blank=True, help_text="คำโปรยหรือข้อความย่อย (ถ้ามี)", null=True
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="รูปภาพปกสำหรับ Hero Section (ควรมีขนาดใหญ่และสัดส่วนแนวนอน เช่น 1600x600px)",
                        upload_to="hero_banners/",
                    ),
                ),
                (
                    "link_url_name",
                    models.CharField(
                        blank=True,
                        help_text="ชื่อ URL pattern ที่จะให้ Banner นี้ลิงก์ไป (เช่น clothes:new_arrivals) ถ้าเว้นว่าง Banner จะไม่เป็นลิงก์",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=False,
                        help_text="เลือก True เพื่อให้ Banner นี้แสดงผล (ควรมี Active แค่อันเดียวต่อครั้ง)",
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="ลำดับการแสดงผล (ถ้ามีหลาย Banner และต้องการเรียง)",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Hero Banner",
                "verbose_name_plural": "Hero Banners",
                "ordering": ["order", "-created_at"],
            },
        ),
    ]
