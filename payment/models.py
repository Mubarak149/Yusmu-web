from django.db import models

# Create your models here.
class Payment(models.Model):
    amount= models.IntegerField()
    reference= models.CharField(max_length=200)
    

    class Meta:
        abstract = True