from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=150, blank=True)
    specialization = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TestInterpretation(models.Model):
    test_name = models.CharField(max_length=300)
    interpretation = models.TextField()
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['test_name']

    def __str__(self):
        return self.test_name
