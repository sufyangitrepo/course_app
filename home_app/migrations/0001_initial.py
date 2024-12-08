# Generated by Django 5.1.4 on 2024-12-06 05:11

import home_app.models
import video_app.libs.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=30)),
                ('course_description', models.TextField()),
                ('is_premium', models.BooleanField(default=False)),
                ('course_img', models.ImageField(blank=True, null=True, storage=video_app.libs.storage.CourseStorage(), upload_to=home_app.models._upload_to)),
                ('slug', models.SlugField(blank=True)),
            ],
        ),
    ]