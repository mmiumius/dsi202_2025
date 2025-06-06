# Generated by Django 5.1.6 on 2025-05-12 06:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clothes", "0006_alter_category_options_alter_clothing_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="clothing",
            name="price",
        ),
        migrations.AddField(
            model_name="clothing",
            name="price_3_days",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="ราคาเช่า 3 วัน (บาท)",
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="clothing",
            name="price_5_days",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="ราคาเช่า 5 วัน (บาท)",
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="clothing",
            name="price_7_days",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="ราคาเช่า 7 วัน (บาท)",
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="clothing",
            name="description",
            field=models.TextField(
                help_text="รายละเอียดชุด, เนื้อผ้า, คำแนะนำในการเช่า (ถ้ามี)"
            ),
        ),
        migrations.AlterField(
            model_name="clothing",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL (สร้างจากชื่ออัตโนมัติ)",
                max_length=120,
                unique=True,
            ),
        ),
    ]
