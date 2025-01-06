# Generated by Django 5.1.2 on 2024-12-27 10:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_student_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprojects',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='student.student'),
        ),
    ]