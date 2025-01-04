from django.contrib import admin
from users.models import UserProjects
from .models import Student,Enrollment,UserProjects
# Register your models here.
admin.site.register([Student, Enrollment,UserProjects])