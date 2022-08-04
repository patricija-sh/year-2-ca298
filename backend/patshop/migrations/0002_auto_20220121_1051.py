# Generated by Django 2.2.12 on 2022-01-21 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patshop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.FileField(null=True, upload_to='products'),
        ),
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('datetime_ordered', models.DateTimeField(auto_now_add=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('basket_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patshop.Basket')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BasketItem',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=1)),
                ('basket_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patshop.Basket')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patshop.Product')),
            ],
        ),
    ]