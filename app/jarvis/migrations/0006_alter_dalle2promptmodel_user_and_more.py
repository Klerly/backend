# Generated by Django 4.1.4 on 2023-01-26 08:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jarvis', '0005_alter_dalle2promptmodel_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dalle2promptmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='dalle2_prompts', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='dalle2promptoutputmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='dalle2_prompt_outputs', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]