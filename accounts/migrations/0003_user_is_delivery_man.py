# Generated by Django 2.2.1 on 2019-07-28 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20190728_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_delivery_man',
            field=models.BooleanField(default=False, verbose_name='Delivery Account'),
        ),
    ]
