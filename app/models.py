from django.db import models

# Create your models here.
class QR_list(models.Model):
    labels = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.labels}"
    