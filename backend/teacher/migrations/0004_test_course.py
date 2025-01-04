# Generated by Django 5.1.2 on 2025-01-01 14:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_delete_studentprojects'),
        ('teacher', '0003_teacher_student_alter_teacherrating_rated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='student.studentcourses'),
        ),
    ]
