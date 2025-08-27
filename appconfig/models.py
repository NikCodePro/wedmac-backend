from django.db import models

class MasterConfig(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()  # <-- use JSONField for nested JSON
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.key
