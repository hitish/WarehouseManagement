# Generated by Django 4.2 on 2023-07-09 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_alter_checked_stock_barcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale_bill',
            name='account_id',
        ),
        migrations.RemoveField(
            model_name='sale_bill',
            name='address_id',
        ),
        migrations.DeleteModel(
            name='product_sold',
        ),
        migrations.DeleteModel(
            name='sale_bill',
        ),
    ]