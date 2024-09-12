from django.db import models


class Comments(models.Model):
    name = models.CharField(max_length=250)
    title = models.CharField(max_length=500)
    comments = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
