# Generated by Django 4.2 on 2023-06-28 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_sale_bill_product_sold'),
    ]

    operations = [
        migrations.AddField(
            model_name='checked_stock',
            name='barcode',
            field=models.FileField(null=True, upload_to='static/barcode/'),
        ),
    ]
