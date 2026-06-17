from django.db import models


class PharmacyItem(models.Model):
    name = models.CharField(max_length=200)
    drug = models.CharField(max_length=200, blank=True)
    unit_type = models.CharField(max_length=20, default='TAB')
    buffer = models.PositiveIntegerField(default=20)
    hsn = models.CharField(max_length=100, blank=True)
    schedule = models.CharField(max_length=50, default='--NA--')
    packing = models.PositiveIntegerField(default=1)
    stock = models.PositiveIntegerField(default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_on_sale = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PharmacyPurchase(models.Model):
    item = models.ForeignKey(PharmacyItem, on_delete=models.CASCADE, related_name='purchases')
    supplier = models.CharField(max_length=200, blank=True)
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)


class PharmacySale(models.Model):
    item = models.ForeignKey(PharmacyItem, on_delete=models.CASCADE, related_name='sales')
    patient_ref = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, default='Cash')
    sold_at = models.DateTimeField(auto_now_add=True)
