# Generated by Django 4.2.6 on 2023-11-15 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captchapractice', '0009_rename_user_name_userresponses_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userresponses',
            name='response_json',
            field=models.JSONField(null=True),
        ),
    ]
