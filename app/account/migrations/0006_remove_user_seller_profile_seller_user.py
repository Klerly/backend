# Generated by Django 4.1.4 on 2023-01-27 23:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_seller_user_seller_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='seller_profile',
        ),
        migrations.AddField(
            model_name='seller',
            name='user',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='seller_profile', to=settings.AUTH_USER_MODEL, verbose_name='Seller Profile'),
            preserve_default=False,
        ),
    ]
