from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_type_data=(
        ('1',"Admin"),
        ('2',"Teacher"),
        ('3',"Student")
        )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    pic = models.ImageField(upload_to='Media/users')
    user_type = models.CharField(choices=user_type_data, max_length=50)


class UserProjects(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=50)
    description = models.TextField()
    url = models.URLField(max_length=300)
    image = models.ImageField(upload_to="Media/Projects")

    def __str__(self):
        return f"{self.title} by {self.user.username}"