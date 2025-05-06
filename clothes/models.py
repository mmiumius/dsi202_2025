from django.db import models

class Clothing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='clothes/')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

