# Generated by Django 4.2.7 on 2023-11-27 10:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_user_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_name', message='Name should not contain numbers or special characters.', regex='^[#](\\w+)$')]),
        ),
    ]
