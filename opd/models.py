from django.db import models
from uhid.models import Patient


class OPDVisit(models.Model):
    PAYMENT_MODES = [('Cash', 'Cash'), ('UPI', 'UPI'), ('Card', 'Card'), ('Cheque', 'Cheque')]

    opd_no = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='opd_visits')
    date = models.DateField()
    time = models.TimeField()
    referral = models.CharField(max_length=200, blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    head = models.CharField(max_length=200, default='Opd Consultation')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='Cash')
    reference_info = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def save(self, *args, **kwargs):
        if not self.opd_no:
            n = OPDVisit.objects.count() + 1
            self.opd_no = f'OPD{n:03d}'
        self.total_amount = max(0, self.fees - self.discount)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.opd_no
