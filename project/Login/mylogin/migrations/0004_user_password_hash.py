# Generated by Django 4.2.18 on 2025-02-13 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mylogin', '0003_remove_user_password_remove_user_registercode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password_hash',
            field=models.CharField(default=None, max_length=200),
            preserve_default=False,
        ),
    ]
