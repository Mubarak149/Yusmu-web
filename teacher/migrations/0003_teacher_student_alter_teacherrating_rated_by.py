# Generated by Django 5.1.2 on 2024-12-27 10:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_alter_studentprojects_student'),
        ('teacher', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='student',
            field=models.ManyToManyField(related_name='teachers', through='teacher.TeacherStudents', to='student.student'),
        ),
        migrations.AlterField(
            model_name='teacherrating',
            name='rated_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student'),
        ),
    ]
