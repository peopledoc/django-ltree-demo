from django.db import models


class Category(models.Model):
    parent = models.ForeignKey('self', null=True, related_name='children',
                               on_delete=models.CASCADE)
    code = models.CharField(max_length=32, unique=True)
    name = models.TextField()
