from django.db import models

# Create your models here.

"""
class EncryptedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    key = models.CharField(max_length=200)
"""

class EncryptedFile(models.Model):
    file = models.BinaryField()
    key = models.CharField(max_length=200)
