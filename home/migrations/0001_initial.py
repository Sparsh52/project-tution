# Generated by Django 4.2.7 on 2023-12-19 17:12

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('is_active', models.BooleanField(default=True)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('name', models.CharField(default='NA', max_length=255)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('phone', models.CharField(default='NA', max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='NotifyRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('institution_type', models.CharField(choices=[('School', 'School'), ('University', 'University')], max_length=10)),
                ('standard_or_semester', models.IntegerField()),
                ('institution_name', models.CharField(max_length=100)),
                ('student_image', models.ImageField(blank=True, null=True, upload_to='student')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.gender')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('teacher_type', models.CharField(choices=[('College', 'College'), ('School', 'School')], max_length=10)),
                ('experience', models.IntegerField()),
                ('min_hourly_rate', models.IntegerField()),
                ('max_hourly_rate', models.IntegerField()),
                ('teacher_image', models.ImageField(blank=True, null=True, upload_to='teacher')),
                ('standard_or_semester', models.IntegerField()),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.gender')),
                ('registered_students', models.ManyToManyField(blank=True, related_name='teachers', to='home.student')),
                ('subject1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers_subject1', to='home.subject')),
                ('subject2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers_subject2', to='home.subject')),
                ('subject3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers_subject3', to='home.subject')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wallet', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_teacher', to='home.wallet')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='wallet',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_student', to='home.wallet'),
        ),
        migrations.CreateModel(
            name='SessionRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('message', models.TextField()),
                ('requested_cost', models.IntegerField(default=0)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_requests', to='home.student')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_requests', to='home.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=100)),
                ('is_seen', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='home.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('event_cost', models.IntegerField(default=0)),
                ('booked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.student')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.teacher')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.notifyroom'),
        ),
    ]
