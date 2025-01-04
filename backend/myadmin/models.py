from django.db import models

# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField("users.CustomUser", on_delete=models.CASCADE)
    designation = models.CharField(max_length=100, blank=True, null=True)  # Job title, e.g., "Principal" or "System Admin"
    permissions = models.JSONField(default=dict, blank=True)  # Custom permissions, e.g., {'can_add_user': True}
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the admin was added
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the admin details were updated

    def __str__(self):
        return self.user.username
