# Generated by Django 4.2.7 on 2023-12-20 07:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionrequest',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 20, 12, 52, 1, 738921)),
        ),
        migrations.AlterField(
            model_name='sessionrequest',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 20, 12, 52, 1, 738921)),
        ),
    ]
