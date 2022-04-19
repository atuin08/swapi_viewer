from django.db import models


class Reports(models.Model):
    guid = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    file_name = models.CharField(max_length=200)
