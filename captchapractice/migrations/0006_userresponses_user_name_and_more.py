# Generated by Django 4.2.6 on 2023-11-14 21:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('captchapractice', '0005_userresponses'),
    ]

    operations = [
        migrations.AddField(
            model_name='userresponses',
            name='user_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userresponses',
            name='root_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='captchapractice.captchaimage'),
        ),
    ]
