from django.db import models

# Create your models here.

class Report(models.Model):
    titulo =  models.CharField(max_length=50)
    descricao = models.CharField(max_length=50)
    impacto = models.CharField(max_length=50)
    risco= models.CharField(max_length=50)
    endpoint = models.CharField(max_length=50)

class SettingsReport(models.Model):
    name =  models.CharField(max_length=50)
