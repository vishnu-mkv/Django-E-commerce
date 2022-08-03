# Generated by Django 3.2.3 on 2022-08-03 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='units_sold',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(choices=[('kg', 'Kilogram'), ('g', 'Gram'), ('l', 'Liter'), ('ml', 'Milliliter'), ('no', 'Number of item'), ('pc', 'Piece')], max_length=10),
        ),
    ]
