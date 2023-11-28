# Generated by Django 4.2.7 on 2023-11-27 09:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_name', message='Name should only contain letters and spaces.', regex='^[a-zA-Z]/$')]),
        ),
    ]