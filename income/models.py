from django.db import models


class IncomeEntry(models.Model):
    CATEGORIES = [
        ('Investigation', 'Investigation'),
        ('OPD', 'OPD'),
        ('IPD', 'IPD'),
        ('Pharmacy', 'Pharmacy'),
    ]
    PAYMENT_MODES = [('Cash', 'Cash'), ('UPI', 'UPI'), ('Card', 'Card'), ('Cheque', 'Cheque')]

    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORIES)
    patient_name = models.CharField(max_length=200)
    description = models.TextField()
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='Cash')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
