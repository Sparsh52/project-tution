# Generated by Django 4.2.7 on 2023-11-29 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_user_name_alter_user_phone_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(default='NA', max_length=255),
        ),
    ]
