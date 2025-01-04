from django.contrib import admin
from .models import Teacher, Test, Question, Answer
# Register your models here.
admin.site.register((Teacher, Test, Question, Answer))