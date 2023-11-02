# Generated by Django 4.2.7 on 2023-11-02 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=100)),
                ('experience', models.IntegerField()),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.gender')),
                ('subject1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers_subject1', to='home.subject')),
                ('subject2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers_subject2', to='home.subject')),
                ('subject3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers_subject3', to='home.subject')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=100)),
                ('institution_type', models.CharField(choices=[('school', 'School'), ('college', 'University')], max_length=10)),
                ('standard_or_semester', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
